"""LINEに送るFlex Messageを組み立てる。"""
from typing import Dict, List

CHOICE_LABELS = ["A", "B", "C", "D", "E"]


def _bubble(index: int, question: Dict, page_url: str) -> Dict:
    choices = [
        {
            "type": "text",
            "text": f"{CHOICE_LABELS[i]}. {choice}",
            "size": "sm",
            "color": "#333333",
            "wrap": True,
            "margin": "sm",
        }
        for i, choice in enumerate(question["choices"])
    ]

    return {
        "type": "bubble",
        "size": "kilo",
        "header": {
            "type": "box",
            "layout": "vertical",
            "backgroundColor": "#2E7D6F",
            "paddingAll": "12px",
            "contents": [
                {"type": "text", "text": f"第{index}問", "color": "#FFFFFF", "size": "sm", "weight": "bold"},
                {"type": "text", "text": question["category"], "color": "#D5EDE7", "size": "xs", "margin": "xs"},
            ],
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "paddingAll": "14px",
            "contents": [
                {"type": "text", "text": question["question"], "size": "sm", "weight": "bold", "wrap": True, "color": "#111111"},
                {"type": "separator", "margin": "md"},
                {"type": "box", "layout": "vertical", "margin": "md", "contents": choices},
            ],
        },
        "footer": {
            "type": "box",
            "layout": "vertical",
            "paddingAll": "12px",
            "contents": [
                {
                    "type": "button",
                    "style": "primary",
                    "color": "#2E7D6F",
                    "height": "sm",
                    "action": {"type": "uri", "label": "答えと解説を見る", "uri": f"{page_url}/q/{question['id']}.html"},
                }
            ],
        },
    }


def build_flex(questions: List[Dict], page_url: str) -> Dict:
    """3問をカルーセル（横スクロール）にまとめる。"""
    return {
        "type": "carousel",
        "contents": [_bubble(i + 1, q, page_url) for i, q in enumerate(questions)],
    }


def build_alt_text(questions: List[Dict], date_label: str, days_left: int) -> str:
    """通知欄に出る代替テキスト。Flexが表示できない環境でも読めるようにしておく。"""
    lines = [f"🥗 NST朝の3問（{date_label}・本番まであと{days_left}日）"]
    for i, q in enumerate(questions, 1):
        lines.append(f"\n第{i}問［{q['category']}］\n{q['question']}")
        for j, choice in enumerate(q["choices"]):
            lines.append(f"{CHOICE_LABELS[j]}. {choice}")
    return "\n".join(lines)
