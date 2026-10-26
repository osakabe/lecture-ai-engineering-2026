from types import SimpleNamespace

import pytest

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

        def create(self, model):
            return FakeChat()

    monkeypatch.setattr(ask_module.genai, "Client", FakeClient)
    monkeypatch.setattr(ask_module, "get_api_key", lambda: "test-key")

    assert ask_module.ask("question") == "answer"
    assert expected in capsys.readouterr().out


def test_main_reuses_chat_for_follow_up_questions(monkeypatch, capsys):
    class FakeChat:
        def __init__(self):
            self.messages = []

        def send_message(self, message):
            self.messages.append(message)
            return SimpleNamespace(
                text=f"answer to {message}",
                usage_metadata=None,
            )

    chat = FakeChat()

    class FakeClient:
        def __init__(self, api_key):
            self.chats = self

        def create(self, model):
            return chat

    questions = iter(["最初の質問", "続けて質問", "終了"])
    monkeypatch.setattr(ask_module.genai, "Client", FakeClient)
    monkeypatch.setattr(ask_module, "get_api_key", lambda: "test-key")
    monkeypatch.setattr("builtins.input", lambda prompt: next(questions))
    monkeypatch.setattr("sys.argv", ["app.ask"])

    ask_module.main()

    assert chat.messages == ["最初の質問", "続けて質問"]
    assert "answer to 続けて質問" in capsys.readouterr().out