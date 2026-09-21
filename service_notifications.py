"""
Backend не хранит aiogram Bot внутри себя постоянно (чтобы не плодить
два инстанса бота с одним токеном), а дергает Telegram Bot API напрямую
через HTTP — это самый простой и надёжный способ слать уведомления
из FastAPI-процесса.
"""

import os
import httpx

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID", "")
TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"


async def _send_message(chat_id: str | int, text: str) -> None:
    if not BOT_TOKEN:
        return
    async with httpx.AsyncClient() as client:
        await client.post(
            f"{TELEGRAM_API}/sendMessage",
            json={"chat_id": chat_id, "text": text, "parse_mode": "HTML"},
        )


async def notify_order_paid(order) -> None:
    user_text = f"✅ Заказ #{order.id} оплачен, спасибо! Скоро приступим к обработке."
    admin_text = (
        f"💰 Новый оплаченный заказ #{order.id}\n"
        f"Сумма: {order.total_amount} грн\n"
        f"Получатель: {order.full_name}, {order.phone}"
    )
    await _send_message(order.user.telegram_id, user_text)
    if ADMIN_CHAT_ID:
        await _send_message(ADMIN_CHAT_ID, admin_text)


async def notify_order_created(order) -> None:
    """Для заказов без онлайн-оплаты (наличные/карта при получении) — уведомляем сразу."""
    user_text = f"🛒 Заказ #{order.id} принят! Статус: новый. Свяжемся с вами для подтверждения."
    admin_text = (
        f"🆕 Новый заказ #{order.id} ({order.payment_method.value})\n"
        f"Сумма: {order.total_amount} грн\n"
        f"Получатель: {order.full_name}, {order.phone}"
    )
    await _send_message(order.user.telegram_id, user_text)
    if ADMIN_CHAT_ID:
        await _send_message(ADMIN_CHAT_ID, admin_text)
