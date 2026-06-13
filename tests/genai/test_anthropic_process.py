import importlib
from types import SimpleNamespace
from typing import Any

import pytest


def test_anthropic_connection_requires_api_key(monkeypatch):  # type: ignore[no-untyped-def]
    # Ensure no ambient API key
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

    anthropic_module = importlib.import_module("cltk.genai.anthropic")
    # Prevent reading from a local .env during the test
    monkeypatch.setattr(anthropic_module, "load_env_file", lambda: None)

    # Provide a benign Anthropic stub so import doesn't error when constructing
    class _AnthropicStub:  # noqa: D401 - trivial stub
        def __init__(self, **_: Any) -> None:
            """No-op Anthropic client stub."""
            pass

    monkeypatch.setattr(anthropic_module, "Anthropic", _AnthropicStub)

    try:
        anthropic_module.AnthropicConnection(model="claude-opus-4-8")
        assert False, "Expected ValueError without API key"
    except ValueError:
        pass


def test_anthropic_connection_uses_env_api_key(monkeypatch):  # type: ignore[no-untyped-def]
    # Supply API key via environment
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")

    anthropic_module = importlib.import_module("cltk.genai.anthropic")

    created = {}

    class _AnthropicRecorder:
        def __init__(self, **kwargs: Any) -> None:  # noqa: D401 - trivial stub
            created.update(kwargs)

    monkeypatch.setattr(anthropic_module, "Anthropic", _AnthropicRecorder)
    conn = anthropic_module.AnthropicConnection(model="claude-opus-4-8")
    assert conn is not None
    assert created.get("api_key") == "test-key"


def test_extract_code_blocks(monkeypatch):  # type: ignore[no-untyped-def]
    anthropic_module = importlib.import_module("cltk.genai.anthropic")

    class _AnthropicStub:
        def __init__(self, **_: Any) -> None:  # noqa: D401 - trivial stub
            pass

    monkeypatch.setattr(anthropic_module, "Anthropic", _AnthropicStub)
    conn = anthropic_module.AnthropicConnection(
        model="claude-opus-4-8", api_key="dummy"
    )

    text = """
Here is some response.

```tsv
FORM	LEMMA	UPOS	FEATS
Lorem	lorem	NOUN	Case=Nom|Number=Sing
```

Some trailing commentary.
"""
    block = conn._extract_code_blocks(text)
    assert block.startswith("FORM\tLEMMA\tUPOS\tFEATS")


def test_build_message_params_model_branching():  # type: ignore[no-untyped-def]
    anthropic_module = importlib.import_module("cltk.genai.anthropic")

    # Claude Opus 4.7+ rejects sampling params; adaptive thinking is sent instead
    opus_params = anthropic_module._build_message_params(
        model="claude-opus-4-8", prompt="p", max_tokens=16000, temperature=0.5
    )
    assert "temperature" not in opus_params
    assert opus_params["thinking"] == {"type": "adaptive"}

    # Older model families still accept temperature; no thinking config sent
    sonnet_params = anthropic_module._build_message_params(
        model="claude-sonnet-4-6", prompt="p", max_tokens=16000, temperature=0.5
    )
    assert sonnet_params["temperature"] == 0.5
    assert "thinking" not in sonnet_params


def _fake_response(
    text: str,
    stop_reason: str = "end_turn",
    input_tokens: int = 10,
    output_tokens: int = 5,
) -> SimpleNamespace:
    return SimpleNamespace(
        content=[SimpleNamespace(type="text", text=text)],
        stop_reason=stop_reason,
        usage=SimpleNamespace(input_tokens=input_tokens, output_tokens=output_tokens),
    )


def test_generate_parses_response_and_usage(monkeypatch):  # type: ignore[no-untyped-def]
    anthropic_module = importlib.import_module("cltk.genai.anthropic")

    response = _fake_response("Intro.\n```tsv\nFORM\tLEMMA\n```\n")

    class _Messages:
        def create(self, **_: Any) -> SimpleNamespace:
            return response

    class _AnthropicStub:
        def __init__(self, **_: Any) -> None:
            self.messages = _Messages()

    monkeypatch.setattr(anthropic_module, "Anthropic", _AnthropicStub)
    conn = anthropic_module.AnthropicConnection(
        model="claude-opus-4-8", api_key="dummy"
    )
    result = conn.generate(prompt="anything")
    assert "FORM" in result.response
    assert result.usage == {"input": 10, "output": 5, "total": 15}


def test_generate_raises_on_refusal(monkeypatch):  # type: ignore[no-untyped-def]
    from cltk.core.exceptions import AnthropicInferenceError

    anthropic_module = importlib.import_module("cltk.genai.anthropic")

    response = _fake_response("", stop_reason="refusal")

    class _Messages:
        def create(self, **_: Any) -> SimpleNamespace:
            return response

    class _AnthropicStub:
        def __init__(self, **_: Any) -> None:
            self.messages = _Messages()

    monkeypatch.setattr(anthropic_module, "Anthropic", _AnthropicStub)
    conn = anthropic_module.AnthropicConnection(
        model="claude-opus-4-8", api_key="dummy"
    )
    with pytest.raises(AnthropicInferenceError):
        conn.generate(prompt="anything")
