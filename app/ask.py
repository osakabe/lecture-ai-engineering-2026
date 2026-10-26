"""第1回: 素のLLMに会話形式で質問するスクリプト。

使い方:
    uv run python -m app.ask "LoRAとは何ですか？"
    uv run python -m app.ask            # 質問を入力し、終了 または Ctrl+C で終了

ツールは使わず、会話履歴を保持する「素の」呼び出し。
講座に固有のことを聞くと、「分からない」と答えるか、一般論でもっともらしく答える
（講座の実際とは違う）ことを確かめよう。
（第3回で、用語集を検索できるエージェントにして改善する）
"""

import argparse
import json
from pathlib import Path

from google import genai
from google.genai import errors
from google.genai import types

from app.config import MODEL, api_error_message, get_api_key

DEFAULT_QUESTION = "AIE2026の講座の宿題にある「3レベル」とは何ですか？"
HISTORY_FILE = Path(__file__).resolve().parent.parent / ".chat_history.json"


def load_history(path: Path | None = None) -> list[types.Content]:
    history_path = path or HISTORY_FILE
    if not history_path.exists():
        return []
    saved_history = json.loads(history_path.read_text(encoding="utf-8"))
    return [types.Content.model_validate(message) for message in saved_history]


def save_history(chat, path: Path | None = None) -> None:
    history_path = path or HISTORY_FILE
    history = [message.model_dump(mode="json", exclude_none=True) for message in chat.get_history()]
    history_path.write_text(
        json.dumps(history, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def create_chat(history: list[types.Content] | None = None):
    client = genai.Client(api_key=get_api_key())
    return client, client.chats.create(model=MODEL, history=history or [])


def ask(question: str, chat=None) -> str:
    if chat is None:
        client, chat = create_chat()
    response = chat.send_message(question)

    usage = response.usage_metadata
    input_tokens = usage.prompt_token_count if usage else None
    output_tokens = usage.candidates_token_count if usage else None
    print(f"[tokens] 入力: {input_tokens if input_tokens is not None else '不明'} / "
          f"出力: {output_tokens if output_tokens is not None else '不明'}")

    return response.text


def main() -> None:
    parser = argparse.ArgumentParser(description="素のLLMに会話形式で質問する")
    parser.add_argument("question", nargs="?", help="最初の質問（省略すると入力待ちになります）")
    args = parser.parse_args()

    print(f"[model] {MODEL}")
    try:
        client, chat = create_chat(load_history())
        if args.question:
            print(f"[質問] {args.question}\n")
            print(ask(args.question, chat))
            save_history(chat)

        while True:
            question = input("質問> ").strip()
            if question.lower() in {"終了", "exit", "quit"}:
                break
            if not question:
                continue
            print(f"[質問] {question}\n")
            print(ask(question, chat))
            save_history(chat)
    except errors.APIError as e:
        print(api_error_message(e.code, e.message))
        raise SystemExit(1)
    except (EOFError, KeyboardInterrupt):
        print("\n終了します")


if __name__ == "__main__":
    main()
