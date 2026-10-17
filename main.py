import asyncio
import logging
from contextlib import asynccontextmanager

from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from database import init_db
import router_products, router_orders, router_payments, router_admin
from config import BOT_TOKEN
import bot_start, bot_admin

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN) if BOT_TOKEN else None
dp = Dispatcher(storage=MemoryStorage())
dp.include_router(bot_start.router)
dp.include_router(bot_admin.router)

_polling_task: asyncio.Task | None = None


async def _run_polling():
    """Бот работает как фоновая задача внутри того же процесса, что и FastAPI —
    это и есть 'всё в одном сервисе' для Render без лишних Web Service'ов."""
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    global _polling_task
    if bot:
        _polling_task = asyncio.create_task(_run_polling())
    else:
        logging.warning("BOT_TOKEN не задан — бот не запущен, работает только API/Mini App")
    yield
    if _polling_task:
        _polling_task.cancel()
    if bot:
        await bot.session.close()


app = FastAPI(title="Telegram Shop Bot", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router_products.router)
app.include_router(router_orders.router)
app.include_router(router_payments.router)
app.include_router(router_admin.router)

# Mini App отдаём тем же сервисом по /webapp — отдельный Static Site на
# Render не нужен, один процесс = один бесплатный сервис
app.mount("/webapp", StaticFiles(directory="webapp", html=True), name="webapp")


@app.get("/")
def health():
    return {"status": "ok"}
