from types import SimpleNamespace

import pytest
from google.genai import types

import app.ask as ask_module


@pytest.mark.parametrize(
    ("usage", "expected"),
    [
        (SimpleNamespace(prompt_token_count=12, candidates_token_count=34), "入力: 12 / 出力: 34"),
        (None, "入力: 不明 / 出力: 不明"),
    ],
)
def test_ask_prints_token_usage(monkeypatch, capsys, usage, expected):
    class FakeChat:
        def send_message(self, message):
            return SimpleNamespace(text="answer", usage_metadata=usage)

    class FakeClient:
        def __init__(self, api_key):
            self.chats = self

        def create(self, model, history):
            return FakeChat()

    monkeypatch.setattr(ask_module.genai, "Client", FakeClient)
    monkeypatch.setattr(ask_module, "get_api_key", lambda: "test-key")

    assert ask_module.ask("question") == "answer"
    assert expected in capsys.readouterr().out


def test_main_loads_saved_history_on_next_run(monkeypatch, capsys, tmp_path):
    class FakeChat:
        def __init__(self, history):
            self.history = list(history)

        def get_history(self):
            return self.history

        def send_message(self, message):
            self.history.extend(
                [
                    types.Content(role="user", parts=[types.Part.from_text(text=message)]),
                    types.Content(role="model", parts=[types.Part.from_text(text=f"answer to {message}")]),
                ]
            )
            return SimpleNamespace(
                text=f"answer to {message}",
                usage_metadata=None,
            )

    chats = []

    class FakeClient:
        def __init__(self, api_key):
            self.chats = self

        def create(self, model, history):
            chat = FakeChat(history)
            chats.append(chat)
            return chat

    monkeypatch.setattr(ask_module.genai, "Client", FakeClient)
    monkeypatch.setattr(ask_module, "get_api_key", lambda: "test-key")
    monkeypatch.setattr(ask_module, "HISTORY_FILE", tmp_path / "history.json")
    monkeypatch.setattr("sys.argv", ["app.ask"])

    questions = iter(["最初の質問", "終了"])
    monkeypatch.setattr("builtins.input", lambda prompt: next(questions))
    ask_module.main()

    questions = iter(["続けて質問", "終了"])
    monkeypatch.setattr("builtins.input", lambda prompt: next(questions))
    ask_module.main()

    assert len(chats) == 2
    assert len(chats[1].history) == 4
    assert chats[1].history[0].parts[0].text == "最初の質問"
    assert chats[1].history[2].parts[0].text == "続けて質問"
    assert "answer to 続けて質問" in capsys.readouterr().out