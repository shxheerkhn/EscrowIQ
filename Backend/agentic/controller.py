"""Bounded Groq controller for read-only hiring recommendations."""

import json

from .registry import AgentToolError


class AgentRunError(RuntimeError):
    pass


class AgentController:
    """Runs a short tool loop and returns a user-facing summary, never reasoning."""

    def __init__(self, completion, max_steps=4):
        self._completion = completion
        self._max_steps = max(1, min(int(max_steps), 6))

    def run(self, prompt, client_id, registry, audit):
        messages = [{"role": "user", "content": self._initial_prompt(prompt, registry)}]
        for step in range(self._max_steps):
            raw = self._completion(messages)
            response = self._parse_response(raw)
            tool_name = response.get("tool")
            if tool_name:
                arguments = response.get("arguments", {})
                if not isinstance(tool_name, str) or not isinstance(arguments, dict):
                    raise AgentRunError("The assistant returned an invalid tool request.")
                try:
                    result = registry.execute(tool_name, arguments, client_id)
                except AgentToolError as exc:
                    audit("tool_rejected", {"tool": tool_name, "reason": str(exc)})
                    messages.append({"role": "assistant", "content": raw})
                    messages.append({
                        "role": "user",
                        "content": json.dumps({
                            "type": "tool_result",
                            "tool": tool_name,
                            "ok": False,
                            "error": str(exc),
                        }),
                    })
                    continue
                audit("tool_used", {"tool": tool_name})
                messages.append({"role": "assistant", "content": raw})
                messages.append({
                    "role": "user",
                    "content": json.dumps({"type": "tool_result", "tool": tool_name, "ok": True, "result": result}),
                })
                continue
            return self._validated_final(response, registry, client_id, audit)
        raise AgentRunError("The assistant reached its step limit. Please try a narrower hiring request.")

    @staticmethod
    def _initial_prompt(prompt, registry):
        return (
            "You are EscrowIQ's hiring assistant and orchestrator. Return JSON only; never output internal planning, waiting, or prose. You can inspect marketplace data only through "
            f"these tools: {json.dumps(registry.tool_descriptions())}. First return a tool and arguments when data is needed. "
            "A tool request must be exactly {\"tool\": string, \"arguments\": object}. After a tool result, either request another valid tool or return the final JSON. "
            "The next user message containing type=tool_result is the actual backend result; never ask to wait for it and never invent it. "
            "When ready return {\"summary\": string, \"propose_acceptance\": {\"proposal_id\": integer} or null}. "
            "Recommend an acceptance only for an existing pending proposal; it requires explicit client approval. "
            "Do not provide hidden reasoning, execute actions, request sensitive data, or invent records. Client request: " + prompt
        )

    @staticmethod
    def _parse_response(raw):
        try:
            value = json.loads(raw)
        except (TypeError, json.JSONDecodeError) as exc:
            raise AgentRunError("The assistant returned an invalid structured response.") from exc
        if not isinstance(value, dict):
            raise AgentRunError("The assistant returned an invalid structured response.")
        return value

    @staticmethod
    def _validated_final(response, registry, client_id, audit):
        summary = response.get("summary", "")
        if not isinstance(summary, str) or not summary.strip() or len(summary) > 4000:
            raise AgentRunError("The assistant response was missing a valid summary.")
        proposed = response.get("propose_acceptance")
        if proposed is None:
            return {"summary": summary.strip(), "proposed_action": None}
        if not isinstance(proposed, dict) or not isinstance(proposed.get("proposal_id"), int):
            raise AgentRunError("The assistant proposed an invalid action.")
        proposal_id = proposed["proposal_id"]
        rows = registry._query_db(
            """
            SELECT p.id FROM proposals p JOIN jobs j ON j.id=p.job_id
            WHERE p.id=? AND p.status='pending' AND j.client_id=?
            """, [proposal_id, client_id], one=True,
        )
        if not rows:
            raise AgentRunError("The proposed proposal is no longer available for approval.")
        action = {"type": "accept_pending_proposal", "proposal_id": proposal_id}
        audit("approval_requested", action)
        return {"summary": summary.strip(), "proposed_action": action}
