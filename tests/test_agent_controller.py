from __future__ import annotations

import json
import unittest

from Backend.agentic.controller import AgentController, AgentRunError


class FakeRegistry:
    def __init__(self):
        self.calls = []
        self._query_db = lambda *_args, **_kwargs: None

    def tool_descriptions(self):
        return {"get_job_candidates": "Rank candidates for an owned open job."}

    def execute(self, tool_name, arguments, client_id):
        self.calls.append((tool_name, arguments, client_id))
        return {"job_id": arguments["job_id"], "candidates": [{"freelancer_id": 7, "match_score": 0.91}]}


class AgentControllerTests(unittest.TestCase):
    def test_sequential_tool_results_are_actual_context_and_final_output_is_valid(self):
        registry = FakeRegistry()
        seen_messages = []

        responses = iter([
            '{"tool":"get_job_candidates","arguments":{"job_id":79}}',
            '{"tool":"get_job_candidates","arguments":{"job_id":79}}',
            '{"summary":"Candidate 7 is the strongest match.","propose_acceptance":null}',
        ])

        def completion(messages):
            seen_messages.append(messages)
            return next(responses)

        result = AgentController(completion, max_steps=4).run(
            "Find the best freelancer for job 79.", 42, registry, lambda *_args: None
        )
        self.assertEqual(result["summary"], "Candidate 7 is the strongest match.")
        self.assertEqual(len(registry.calls), 2)
        second_request = seen_messages[1]
        self.assertEqual(second_request[-2]["role"], "assistant")
        self.assertEqual(json.loads(second_request[-1]["content"]), {
            "type": "tool_result",
            "tool": "get_job_candidates",
            "ok": True,
            "result": {"job_id": 79, "candidates": [{"freelancer_id": 7, "match_score": 0.91}]},
        })

    def test_waiting_prose_is_rejected_and_never_accepted_as_a_step(self):
        registry = FakeRegistry()
        with self.assertRaises(AgentRunError):
            AgentController(lambda _messages: "[The assistant should now wait for the tool's response.] ").run(
                "Find a freelancer.", 42, registry, lambda *_args: None
            )


if __name__ == "__main__":
    unittest.main()