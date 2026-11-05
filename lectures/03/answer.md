# 第3回 解答

## 演習

- 第1回（素のLLM）とエージェントの回答の違い：
  素のLLMは一般論で回答するが、今回（第3回）のエージェントは用語集（glossary.json）に近い回答を行っている。しかし、用語集にはない情報を加えて回答を行っている。（例：基礎：講義内容の確認（**知識の定着を目的とする**））また、システムプロンプトの指示どおりに回答の最後に関係する回として第1回を出力している。
- `--trace` で見えたツール呼び出し（ツール名と引数）：
  ```text
  search_glossary({'query': 'LoRA'})
  search_glossary({'query': 'QLoRA'})
  ```
- 1つの質問での LLM 呼び出し回数（`requests`）：2回
- 追加したツールと、docstring に書いた説明：
  - 追加したツール: make_quiz
  - docstring:
    指定した回の用語から 1つを選び、確認問題と答えを返す。「第2回の確認問題を出して」のように、復習用の問題を求められたときに使う。

## 宿題

- 取り組んだレベル：発展
- やったこと：
  演習のエージェントと同じ指示とツールを使い、エージェントを組み立てる部分だけをGoogle の ADKで書き直し、adk run で動かして、書き方や回答を比べた。

- 結果：
  - 書き方：
    - 指示の渡し方：
      Pydantic AIもGoogle ADKもAgentインスタンスを作成する際に、指示（システムプロンプト（INSTRUCTIONS））を渡す。
    - ツールの渡し方：
      Pydantic AIは、Agentインスタンスのtool_plain関数でツールを渡す。Google ADKはAgentインスタンス作成時にツールを渡す。
  - 質問への回答：
      回答はPydantic AIでもGoogle ADKでも同様の内容である。

- 気づき・疑問：
  - Google ADKの場合、モデルが混雑していて使えないエラー（503）の場合に長いエラーログが出力されて、アプリが落ちる。
  - GEMINI_API_KEYについて、Pydantic AIでは明示的に取得してエージェントに渡しているが、Google ADKでは明示的には与えていない。Google ADKは環境変数GEMINI_API_KEYを自動で読み込んでいる。
  - Google ADKでツール呼び出し時に承認を要求するには、FunctionTool をインポートする。承認が必要なツールを require_confirmation=True を指定してFunctionToolで包み、Agent の tools に登録する。
  使用したGoogle ADK（2.13.0）では、承認が必要なツールを登録すると、実行時に承認を求める動作を確認できた。一方、Pydantic AIでは、アプリケーション側で承認要求を受け取り、承認結果を渡して処理を再開するコードが必要だった。