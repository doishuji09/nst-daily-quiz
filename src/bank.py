"""問題バンクの読み込みと、その日の出題を選ぶ処理。"""
import glob
import json
import os
from typing import Dict, List

BANK_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "bank")
HISTORY_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "history.json")


def load_bank() -> List[Dict]:
    """data/bank/ 配下のJSONをすべて読み込み、1つのリストにまとめる。"""
    questions: List[Dict] = []
    seen = set()
    for path in sorted(glob.glob(os.path.join(BANK_DIR, "*.json"))):
        with open(path, encoding="utf-8") as f:
            for q in json.load(f):
                if q["id"] in seen:
                    raise ValueError(f"問題IDが重複しています: {q['id']}")
                seen.add(q["id"])
                questions.append(q)
    if not questions:
        raise ValueError("問題バンクが空です。data/bank/ にJSONを置いてください。")
    return questions


def load_history() -> Dict:
    """出題履歴を読み込む。無ければ空の履歴を返す。"""
    if not os.path.exists(HISTORY_PATH):
        return {"sent_ids": [], "log": {}}
    with open(HISTORY_PATH, encoding="utf-8") as f:
        return json.load(f)


def save_history(history: Dict) -> None:
    with open(HISTORY_PATH, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)
        f.write("\n")


def pick_questions(questions: List[Dict], history: Dict, count: int = 3) -> List[Dict]:
    """未出題の中からcount問を選ぶ。

    同じ日に同じカテゴリが偏らないよう、未出題のカテゴリを順に拾っていく。
    未出題が尽きた場合は、出題が古いものから再度出す（試験直前の復習用）。
    """
    sent = set(history.get("sent_ids", []))
    unsent = [q for q in questions if q["id"] not in sent]

    if len(unsent) < count:
        # 一周したら、出題順が古いものから復習として出し直す
        order = {qid: i for i, qid in enumerate(history.get("sent_ids", []))}
        pool = unsent + sorted(
            (q for q in questions if q["id"] in sent),
            key=lambda q: order.get(q["id"], 0),
        )
        return pool[:count]

    picked: List[Dict] = []
    used_categories: set = set()
    for q in unsent:
        if q["category"] not in used_categories:
            picked.append(q)
            used_categories.add(q["category"])
        if len(picked) == count:
            return picked

    # カテゴリを散らしきれなければ、残りは未出題の先頭から埋める
    for q in unsent:
        if q not in picked:
            picked.append(q)
        if len(picked) == count:
            break
    return picked
