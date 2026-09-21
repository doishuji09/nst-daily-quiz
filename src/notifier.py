import os
import requests
from typing import Optional, Dict

LINE_PUSH_URL = "https://api.line.me/v2/bot/message/push"
LINE_MAX_LENGTH = 5000


def _credentials(token: Optional[str], user_id: Optional[str]) -> tuple:
    """トークンと送信先を環境変数から補完する。"""
    if token is None:
        token = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")
    if user_id is None:
        user_id = os.environ.get("LINE_USER_ID")

    if not token:
        raise ValueError("LINE_CHANNEL_ACCESS_TOKEN が設定されていません。")
    if not user_id:
        raise ValueError("LINE_USER_ID が設定されていません。")

    return token, user_id


def _push(message: Dict, token: str, user_id: str) -> bool:
    """Push Message APIを1回叩く。"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    body = {"to": user_id, "messages": [message]}

    try:
        response = requests.post(LINE_PUSH_URL, headers=headers, json=body, timeout=10)
        if response.status_code == 200:
            return True
        print(f"  LINE通知エラー: ステータスコード {response.status_code} - {response.text}")
        return False
    except requests.RequestException as e:
        print(f"  LINE通知エラー: 通信に失敗しました - {e}")
        return False


def send_line_flex(
    alt_text: str,
    contents: Dict,
    token: Optional[str] = None,
    user_id: Optional[str] = None,
) -> bool:
    """Flex MessageをLINEに送信する。

    Args:
        alt_text: プッシュ通知欄などに出る代替テキスト（最大400文字）
        contents: Flexのバブル定義
        token: チャンネルアクセストークン（省略時は環境変数から取得）
        user_id: 送信先のユーザーID（省略時は環境変数から取得）

    Returns:
        送信成功時はTrue、失敗時はFalse
    """
    token, user_id = _credentials(token, user_id)

    message = {
        "type": "flex",
        "altText": alt_text[:400],
        "contents": contents,
    }
    return _push(message, token, user_id)


def send_line_message(message: str, token: Optional[str] = None, user_id: Optional[str] = None) -> bool:
    """LINE Messaging API（Push Message）でメッセージを送信する。

    Args:
        message: 送信するメッセージ（最大5000文字）
        token: チャンネルアクセストークン（省略時は環境変数から取得）
        user_id: 送信先のユーザーID（省略時は環境変数から取得）

    Returns:
        送信成功時はTrue、失敗時はFalse
    """
    token, user_id = _credentials(token, user_id)

    # 5000文字を超える場合は末尾を切り詰める
    if len(message) > LINE_MAX_LENGTH:
        message = message[:LINE_MAX_LENGTH - 3] + "..."

    return _push({"type": "text", "text": message}, token, user_id)


def send_line_messages(messages: list, token: Optional[str] = None, user_id: Optional[str] = None) -> bool:
    """複数のメッセージを1回のPushでまとめて送る（LINEは1回5通まで）。"""
    token, user_id = _credentials(token, user_id)

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    body = {"to": user_id, "messages": messages[:5]}

    try:
        response = requests.post(LINE_PUSH_URL, headers=headers, json=body, timeout=10)
        if response.status_code == 200:
            return True
        print(f"  LINE通知エラー: ステータスコード {response.status_code} - {response.text}")
        return False
    except requests.RequestException as e:
        print(f"  LINE通知エラー: 通信に失敗しました - {e}")
        return False
