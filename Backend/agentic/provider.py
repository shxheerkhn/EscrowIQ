"""Groq provider for the EscrowIQ agent's structured completion loop."""

from __future__ import annotations

import os


class AgentProviderError(RuntimeError):
    """Raised when Groq cannot return a usable agent completion."""


class GroqAgentProvider:
    """Groq completion client kept outside the controller."""

    def __init__(self, client_factory=None, api_key=None, model=None, timeout=None):
        self.api_key = (api_key if api_key is not None else os.environ.get("GROQ_API_KEY", "")).strip()
        self.model = (model if model is not None else os.environ.get("GROQ_MODEL", "")).strip()
        self.timeout = timeout if timeout is not None else self._timeout_from_environment()
        self._client_factory = client_factory

    @staticmethod
    def _timeout_from_environment():
        try:
            return max(1, int(os.environ.get("AGENT_GROQ_TIMEOUT_SECONDS", "20")))
        except ValueError:
            return 20

    def __call__(self, messages):
        if not self.api_key:
            raise AgentProviderError("GROQ_API_KEY is not configured on the server yet.")
        if not self.model:
            raise AgentProviderError("GROQ_MODEL is not configured on the server yet.")
        try:
            if self._client_factory is None:
                from groq import Groq
                self._client_factory = lambda: Groq(api_key=self.api_key, timeout=self.timeout)
            response = self._client_factory().chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0,
                max_completion_tokens=900,
                response_format={"type": "json_object"},
                stream=False,
            )
            content = response.choices[0].message.content
        except AgentProviderError:
            raise
        except Exception as exc:
            raise AgentProviderError(f"Groq agent request failed: {exc}") from exc
        if not isinstance(content, str) or not content.strip():
            raise AgentProviderError("Groq returned an empty agent response.")
        return content.strip()
