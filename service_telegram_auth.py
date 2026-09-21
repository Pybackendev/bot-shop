"""
Проверка подлинности initData, которую Telegram Mini App передаёт на бэкенд.

Без этой проверки любой человек может слать на /api/order произвольные
запросы, притворяясь, что они из Telegram. Алгоритм — официальный,
описан в доке Telegram: https://core.telegram.org/bots/webapps#validating-data-received-via-the-mini-app
"""

import hashlib
import hmac
import json
import os
from urllib.parse import parse_qsl

from fastapi import HTTPException, Header

BOT_TOKEN = os.getenv("BOT_TOKEN", "")


def _check_signature(init_data: str, bot_token: str) -> dict:
    parsed = dict(parse_qsl(init_data, strict_parsing=True))
    received_hash = parsed.pop("hash", None)
    if not received_hash:
        raise ValueError("no hash in initData")

    data_check_string = "\n".join(
        f"{k}={v}" for k, v in sorted(parsed.items())
    )

    secret_key = hmac.new(
        key=b"WebAppData", msg=bot_token.encode(), digestmod=hashlib.sha256
    ).digest()
    calculated_hash = hmac.new(
        key=secret_key, msg=data_check_string.encode(), digestmod=hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(calculated_hash, received_hash):
        raise ValueError("signature mismatch")

    return parsed


def get_telegram_user(x_telegram_init_data: str = Header(..., alias="X-Telegram-Init-Data")) -> dict:
    """
    FastAPI dependency: провалидировать initData из заголовка запроса
    и вернуть данные юзера (telegram_id, username, full_name).

    Использование в роутере:
        @router.post("/order")
        def create_order(..., tg_user: dict = Depends(get_telegram_user)):
    """
    if not BOT_TOKEN:
        raise HTTPException(500, "BOT_TOKEN is not configured on server")

    try:
        parsed = _check_signature(x_telegram_init_data, BOT_TOKEN)
    except ValueError as e:
        raise HTTPException(401, f"invalid Telegram initData: {e}")

    user_raw = parsed.get("user")
    if not user_raw:
        raise HTTPException(401, "no user field in initData")

    user = json.loads(user_raw)
    return {
        "telegram_id": user["id"],
        "username": user.get("username"),
        "full_name": f"{user.get('first_name', '')} {user.get('last_name', '')}".strip(),
    }
