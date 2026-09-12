from __future__ import annotations

import unittest

from Backend.agentic.provider import AgentProviderError, GroqAgentProvider


class FakeCompletion:
    def __init__(self, content):
        self.choices = [type("Choice", (), {"message": type("Message", (), {"content": content})()})()]


class FakeClient:
    def __init__(self, content='{"summary":"ok"}', error=None):
        self.content = content
        self.error = error
        self.chat = type("Chat", (), {})()
        self.chat.completions = type("Completions", (), {"create": self.create})()

    def create(self, **kwargs):
        if self.error:
            raise self.error
        self.kwargs = kwargs
        return FakeCompletion(self.content)


class GroqProviderTests(unittest.TestCase):
    def test_uses_groq_credentials_model_and_structured_output(self):
        client = FakeClient()
        provider = GroqAgentProvider(
            client_factory=lambda: client,
            api_key="test-key",
            model="openai/gpt-oss-120b",
        )
        self.assertEqual(provider([{"role": "user", "content": "Review jobs"}]), '{"summary":"ok"}')
        self.assertEqual(client.kwargs["model"], "openai/gpt-oss-120b")
        self.assertEqual(client.kwargs["response_format"], {"type": "json_object"})

    def test_missing_credentials_fail_without_client_creation(self):
        provider = GroqAgentProvider(client_factory=lambda: self.fail("client created"), api_key="", model="model")
        with self.assertRaisesRegex(AgentProviderError, "GROQ_API_KEY"):
            provider([])

    def test_missing_model_and_empty_response_are_rejected(self):
        with self.assertRaisesRegex(AgentProviderError, "GROQ_MODEL"):
            GroqAgentProvider(client_factory=lambda: FakeClient(), api_key="key", model="")([])
        provider = GroqAgentProvider(client_factory=lambda: FakeClient(content=""), api_key="key", model="model")
        with self.assertRaisesRegex(AgentProviderError, "empty"):
            provider([])

    def test_provider_errors_are_wrapped(self):
        provider = GroqAgentProvider(
            client_factory=lambda: FakeClient(error=RuntimeError("provider unavailable")),
            api_key="key",
            model="model",
        )
        with self.assertRaisesRegex(AgentProviderError, "Groq agent request failed"):
            provider([])


if __name__ == "__main__":
    unittest.main()
