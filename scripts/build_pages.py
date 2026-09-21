"""問題バンクから、解説ページ（docs/q/*.html）を生成する。

問題を追加・修正したら、このスクリプトを実行してコミットする。
GitHub Pages が docs/ を公開するので、LINEのボタンからそのまま開ける。
"""
import html
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from bank import load_bank

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS_Q = os.path.join(ROOT, "docs", "q")
LABELS = ["A", "B", "C", "D", "E"]

PAGE = """<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex">
<title>{title}</title>
<style>
  :root {{
    --bg: #f6f8f7; --card: #ffffff; --text: #1b1f1e; --muted: #5d6b67;
    --accent: #2e7d6f; --accent-soft: #e4f1ed; --line: #dfe6e3;
  }}
  @media (prefers-color-scheme: dark) {{
    :root {{
      --bg: #121615; --card: #1b2220; --text: #e8efec; --muted: #9aa8a3;
      --accent: #5cbfa9; --accent-soft: #23332f; --line: #2c3634;
    }}
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0; padding: 20px 16px 48px; background: var(--bg); color: var(--text);
    font-family: -apple-system, BlinkMacSystemFont, "Hiragino Sans", "Noto Sans JP", sans-serif;
    line-height: 1.75; -webkit-text-size-adjust: 100%;
  }}
  main {{ max-width: 620px; margin: 0 auto; }}
  .tag {{
    display: inline-block; background: var(--accent-soft); color: var(--accent);
    font-size: 12px; font-weight: 700; padding: 4px 10px; border-radius: 999px;
  }}
  h1 {{ font-size: 18px; line-height: 1.6; margin: 14px 0 20px; }}
  .card {{
    background: var(--card); border: 1px solid var(--line); border-radius: 14px;
    padding: 18px; margin-bottom: 16px;
  }}
  ol {{ margin: 0; padding-left: 0; list-style: none; }}
  li {{
    padding: 10px 12px; border-radius: 10px; margin-bottom: 8px;
    border: 1px solid var(--line); font-size: 15px;
  }}
  li.correct {{ border-color: var(--accent); background: var(--accent-soft); font-weight: 700; }}
  li .mark {{ color: var(--accent); font-weight: 700; margin-right: 6px; }}
  details > summary {{
    list-style: none; cursor: pointer; text-align: center; background: var(--accent);
    color: #fff; font-weight: 700; padding: 13px; border-radius: 10px; font-size: 15px;
  }}
  details > summary::-webkit-details-marker {{ display: none; }}
  details[open] > summary {{ display: none; }}
  h2 {{ font-size: 14px; color: var(--muted); margin: 22px 0 8px; letter-spacing: .04em; }}
  p.explanation {{ margin: 0; font-size: 15px; }}
  footer {{ text-align: center; color: var(--muted); font-size: 12px; margin-top: 28px; }}
</style>
</head>
<body>
<main>
  <span class="tag">{category}</span>
  <h1>{question}</h1>
  <details>
    <summary>答えと解説を見る</summary>
    <div class="card">
      <ol>{choices}</ol>
    </div>
    <h2>解説</h2>
    <div class="card">
      <p class="explanation">{explanation}</p>
    </div>
  </details>
  <footer>{qid} ・ NST朝の3問</footer>
</main>
</body>
</html>
"""

INDEX = """<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex">
<title>NST朝の3問</title>
<style>
  body {{ margin: 0; padding: 48px 20px; background: #f6f8f7; color: #1b1f1e;
    font-family: -apple-system, BlinkMacSystemFont, "Hiragino Sans", "Noto Sans JP", sans-serif;
    line-height: 1.8; text-align: center; }}
  @media (prefers-color-scheme: dark) {{ body {{ background: #121615; color: #e8efec; }} }}
  main {{ max-width: 520px; margin: 0 auto; }}
  h1 {{ font-size: 20px; }}
  p {{ font-size: 15px; }}
</style>
</head>
<body>
<main>
  <h1>🥗 NST朝の3問</h1>
  <p>毎朝7時にLINEへ3問届きます。<br>解説は、届いたメッセージのボタンから開いてください。</p>
  <p>収録問題数：{count}問</p>
</main>
</body>
</html>
"""


def main() -> None:
    questions = load_bank()
    os.makedirs(DOCS_Q, exist_ok=True)

    for q in questions:
        choices = "".join(
            '<li class="{cls}">{mark}{label}. {text}</li>'.format(
                cls="correct" if i == q["answer"] else "",
                mark='<span class="mark">正解</span>' if i == q["answer"] else "",
                label=LABELS[i],
                text=html.escape(choice),
            )
            for i, choice in enumerate(q["choices"])
        )
        page = PAGE.format(
            title=f"{q['id']} ｜ NST朝の3問",
            category=html.escape(q["category"]),
            question=html.escape(q["question"]),
            choices=choices,
            explanation=html.escape(q["explanation"]),
            qid=q["id"],
        )
        with open(os.path.join(DOCS_Q, f"{q['id']}.html"), "w", encoding="utf-8") as f:
            f.write(page)

    with open(os.path.join(ROOT, "docs", "index.html"), "w", encoding="utf-8") as f:
        f.write(INDEX.format(count=len(questions)))

    print(f"{len(questions)} 問の解説ページを生成しました → docs/q/")


if __name__ == "__main__":
    main()
