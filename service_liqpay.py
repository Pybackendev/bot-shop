"""
Интеграция с LiqPay: создание платежа и проверка подписи callback'а.
Доки: https://www.liqpay.ua/documentation/api/aquiring/checkout/doc
"""

import base64
import hashlib
import hmac
import json
import os

LIQPAY_PUBLIC_KEY = os.getenv("LIQPAY_PUBLIC_KEY", "")
LIQPAY_PRIVATE_KEY = os.getenv("LIQPAY_PRIVATE_KEY", "")
BACKEND_URL = os.getenv("RENDER_EXTERNAL_URL", "http://localhost:8000")


def _encode_params(params: dict) -> str:
    return base64.b64encode(json.dumps(params).encode()).decode()


def _make_signature(data_b64: str) -> str:
    raw = LIQPAY_PRIVATE_KEY + data_b64 + LIQPAY_PRIVATE_KEY
    return base64.b64encode(hashlib.sha1(raw.encode()).digest()).decode()


def create_payment_link(order_id: str, amount: float, description: str) -> str:
    """
    Возвращает URL чекаута LiqPay (checkout.liqpay.ua/api/3/checkout),
    на который фронт редиректит юзера (или открывает через Telegram.WebApp.openLink).
    """
    params = {
        "public_key": LIQPAY_PUBLIC_KEY,
        "version": "3",
        "action": "pay",
        "amount": amount,
        "currency": "UAH",
        "description": description,
        "order_id": order_id,
        "server_url": f"{BACKEND_URL}/api/webhook/payment",
    }
    data = _encode_params(params)
    signature = _make_signature(data)
    return f"https://www.liqpay.ua/api/3/checkout?data={data}&signature={signature}"


def verify_callback(data_b64: str, signature: str) -> dict:
    """
    Проверяет подпись webhook-запроса от LiqPay.
    Бросает ValueError, если подпись не совпала — такой запрос доверять нельзя.
    """
    expected_signature = _make_signature(data_b64)
    if not hmac.compare_digest(expected_signature, signature):
        raise ValueError("LiqPay signature mismatch — possibly forged request")

    decoded = json.loads(base64.b64decode(data_b64))
    return decoded
