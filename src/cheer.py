"""毎朝の応援メッセージを選ぶ。

文面には個人名が入るため、公開リポジトリには置かない。
本番は環境変数 CHEERS_JSON（GitHub Secrets）から、手元では data/cheers.json（git管理外）から読む。
どちらも無ければ、名前を含まない汎用の一言に落として送信は止めない。
"""
import hashlib
import json
import os
import random
from typing import Dict

CHEERS_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "cheers.json")

FALLBACK_CHEER = "今日の3問、いってみよう。"


def load_cheers() -> Dict:
    """CHEERS_JSON → data/cheers.json の順に探す。見つからなければ空を返す。"""
    raw = os.environ.get("CHEERS_JSON")
    if raw:
        return json.loads(raw)
    if os.path.exists(CHEERS_PATH):
        with open(CHEERS_PATH, encoding="utf-8") as f:
            return json.load(f)
    print("  警告: 応援メッセージが見つかりません（CHEERS_JSON も data/cheers.json も無し）。汎用の一言で送ります。")
    return {}


def _key(text: str) -> str:
    """使用済みの記録用に、本文の代わりに短いハッシュを残す。

    履歴（data/history.json）は公開リポジトリにコミットされるため、本文は書かない。
    """
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[:8]


def pick_cheer(history: Dict, days_left: int) -> str:
    """その日の応援メッセージを1つ返す。

    残り日数が節目の日は専用のメッセージを出す。
    それ以外は通常のメッセージから、まだ使っていないものをランダムに選ぶ。
    全部使い切ったら履歴をリセットして一周目に戻る。
    """
    cheers = load_cheers()
    if not cheers:
        return FALLBACK_CHEER

    if days_left < 0:
        return random.choice(cheers.get("after") or [FALLBACK_CHEER])

    milestone = cheers.get("milestones", {}).get(str(days_left))
    if milestone:
        return milestone

    daily = cheers.get("daily") or [FALLBACK_CHEER]
    used = set(history.get("used_cheers", []))
    remaining = [c for c in daily if _key(c) not in used]
    if not remaining:
        history["used_cheers"] = []
        remaining = daily

    chosen = random.choice(remaining)
    history.setdefault("used_cheers", []).append(_key(chosen))
    return chosen
