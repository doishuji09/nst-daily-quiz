"""毎朝、NSTの問題を3問LINEに送る。"""
import os
import sys
from datetime import date, datetime, timedelta, timezone

try:
    from dotenv import load_dotenv
except ImportError:  # .env を使わない環境（GitHub Actions など）では無くてもよい
    def load_dotenv():
        return False

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bank import load_bank, load_history, pick_questions, save_history
from cheer import pick_cheer
from formatter import build_alt_text, build_flex
from notifier import send_line_messages

JST = timezone(timedelta(hours=9))
EXAM_DATE = date(2026, 10, 11)
WEEKDAYS = ["月", "火", "水", "木", "金", "土", "日"]
DEFAULT_PAGE_URL = "https://doishuji09.github.io/nst-daily-quiz"


def main() -> int:
    load_dotenv()
    page_url = os.environ.get("QUIZ_PAGES_BASE_URL", DEFAULT_PAGE_URL).rstrip("/")
    dry_run = "--dry-run" in sys.argv
    test = "--test" in sys.argv  # 実際に送るが、出題履歴は進めない（動作確認用）

    today = datetime.now(JST).date()
    days_left = (EXAM_DATE - today).days
    date_label = f"{today.month}/{today.day}（{WEEKDAYS[today.weekday()]}）"

    questions = load_bank()
    history = load_history()

    if not test and history.get("log", {}).get(today.isoformat()):
        print(f"{today} はすでに出題済みです。送信をスキップします。")
        return 0

    if test:
        # 本番の初日以降の出題を先取りしないよう、バンクの末尾から出す
        picked = questions[-3:]
    else:
        picked = pick_questions(questions, history, count=3)
    print(f"出題: {[q['id'] for q in picked]}（残り未出題 {len(questions) - len(history.get('sent_ids', [])) - len(picked)} 問）")

    cheer = pick_cheer(history, days_left)
    if days_left > 0:
        countdown = f"本番まであと{days_left}日"
    elif days_left == 0:
        countdown = "今日が本番"
    else:
        countdown = "復習モード"
    lead = f"🥗 NST朝の3問｜{date_label}・{countdown}\n\n{cheer}"
    if test:
        lead = "【テスト送信】明日から本番の配信が始まります。\n\n" + lead

    messages = [
        {"type": "text", "text": lead},
        {
            "type": "flex",
            "altText": build_alt_text(picked, date_label, days_left)[:400],
            "contents": build_flex(picked, page_url),
        },
    ]

    if dry_run:
        import json
        print(json.dumps(messages, ensure_ascii=False, indent=2))
        return 0

    if not send_line_messages(messages):
        print("送信に失敗しました。履歴は更新しません。")
        return 1

    if test:
        print("テスト送信しました（出題履歴は更新しません）。")
        return 0

    history.setdefault("sent_ids", []).extend(q["id"] for q in picked)
    history.setdefault("log", {})[today.isoformat()] = [q["id"] for q in picked]
    save_history(history)
    print("送信しました。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
