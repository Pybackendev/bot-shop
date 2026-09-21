from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

from .config import WEBAPP_URL

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🛍 Открыть магазин", web_app=WebAppInfo(url=WEBAPP_URL))]
        ]
    )
    await message.answer(
        "Привет! Это магазин прямо в Telegram 🛒\n"
        "Жми кнопку ниже, чтобы посмотреть каталог и оформить заказ.",
        reply_markup=keyboard,
    )
