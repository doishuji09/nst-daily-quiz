# NST朝の3問

NST（栄養サポートチーム）の資格試験に向けて、**毎朝7時（JST）に3問だけLINEへ届く**仕組み。
問題はLINEのメッセージで読み、答えと解説はボタンから開くWebページ（GitHub Pages）で確認する。

GitHub Actions の cron で動くのでサーバー不要・無料。

- 試験日：2026年10月11日（`src/main.py` の `EXAM_DATE`）
- 収録問題数：60問（19日ぶん × 3問）

## 仕組み

```
data/bank/*.json   問題バンク（問題・選択肢・正解・解説）
data/cheers.json   応援メッセージ（git管理外。本番は GitHub Secret の CHEERS_JSON から読む）
      │
      ├─ scripts/build_pages.py → docs/q/qNNN.html   解説ページ（GitHub Pagesで公開）
      │
      └─ src/main.py（毎朝7時）
             ├─ data/history.json を見て、未出題から3問選ぶ（カテゴリが偏らないように）
             ├─ LINEへ2通送る（応援メッセージ＋3問のカルーセル）
             └─ 出題履歴を data/history.json に記録してコミット
```

解説ページは事前に生成してあるので、配信のたびにビルドを待つ必要がない。
ページを開いてもすぐには答えが見えず、「答えと解説を見る」をタップして初めて表示される。

## セットアップ

### 1. LINEの送信先を用意する

1. 送る相手に、LINE公式アカウント（Messaging APIのチャネル）を**友だち追加**してもらう
2. その人の userId を取得する（Webhook で受け取るか、LINE Developers のコンソールで確認する）
3. GitHubリポジトリの Settings → Secrets and variables → Actions に登録する

| 種別 | 名前 | 中身 |
| --- | --- | --- |
| Secret | `LINE_CHANNEL_ACCESS_TOKEN` | チャネルアクセストークン（長期） |
| Secret | `LINE_USER_ID` | 送信先の userId（`U` から始まる文字列） |
| Secret | `CHEERS_JSON` | 応援メッセージ（`data/cheers.json` の中身そのまま。個人名が入るため公開リポジトリには置かない） |
| Variable | `QUIZ_PAGES_BASE_URL` | 例：`https://doishuji09.github.io/nst-daily-quiz` |

### 2. GitHub Pages を有効にする

Settings → Pages → Source を `Deploy from a branch`、ブランチを `main`、フォルダを `/docs` にする。
公開URLを上の `QUIZ_PAGES_BASE_URL` に設定する。

### 3. 動作確認

```bash
python src/main.py --dry-run   # 送らずに、送信内容を表示するだけ
python src/main.py             # 実際にLINEへ送る（履歴も更新される）
```

GitHubの Actions タブから `Daily NST Quiz` を手動実行しても確認できる。
「Run workflow」で **test にチェック**を入れると、テスト送信になる（バンク末尾の3問を送り、出題履歴は進めない）。
```bash
gh workflow run daily_quiz.yml -f test=true
```

## 問題を追加・修正する

`data/bank/` にJSONを足すか、既存のファイルを編集する。IDは全体で重複しないようにする。

```json
{
  "id": "q061",
  "category": "栄養評価",
  "question": "問題文",
  "choices": ["選択肢A", "選択肢B", "選択肢C", "選択肢D"],
  "answer": 1,
  "explanation": "解説。なぜ他の選択肢が誤りかまで書く。"
}
```

`answer` は正解の選択肢の**インデックス（0始まり）**。編集したら解説ページを作り直す。

```bash
python scripts/build_pages.py
git add -A && git commit -m "問題を追加" && git push
```

## 設計上の判断

- **問題は事前に作って貯める**。毎朝APIで生成する案もあったが、栄養の専門知識は誤りが混じったときに
  そのまま覚えてしまうため、中身を事前に確認できる形にした。
- **解説はLINE本文に書かず、別ページにした**。同じメッセージに書くと答えが目に入ってしまう。
- **解説ページは事前生成**。配信時に生成してコミットする方式だと、Pagesのビルドが終わる前に
  ボタンを押されて404になりうる。
- **1日1回まで**。`data/history.json` の `log` に日付を記録し、同じ日の二重送信を防いでいる。
- 未出題が尽きたら、出題が古いものから再出題する（試験直前の復習用）。
- **応援メッセージは使ったものを記録し、一周するまで繰り返さない**。毎朝同じ言葉が届くと
  自動送信だと気づかれて響かなくなるため。残り14日・7日・3日・2日・1日・当日は専用の文面に切り替わる。

### 応援メッセージを書き換える

このリポジトリは公開なので、個人名が入る応援文はリポジトリに置かない。
手元の `data/cheers.json`（`.gitignore` 済み）を編集して、Secretを更新する。

```bash
gh secret set CHEERS_JSON < data/cheers.json
```

`daily` に足すだけでよく、`milestones` のキーは試験までの残り日数。
使用済みの記録（`data/history.json` の `used_cheers`）は本文ではなく短いハッシュで持つ。
文面を直すとハッシュも変わり、直した文は未使用として扱われる。
Secretが未設定でも送信は止まらず、名前を含まない「今日の3問、いってみよう。」に落ちる。
