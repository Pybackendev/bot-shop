# Telegram Shop

Telegram-магазин с каталогом, корзиной и оформлением заказа в Mini App. Покупатель выбирает товары в Telegram, а администратор управляет ассортиментом и заказами через бота.

**Python · aiogram 3 · FastAPI · SQLAlchemy · SQLite/PostgreSQL · LiqPay**

## Возможности

- Каталог товаров с описанием, ценой, остатком и фотографией.
- Корзина и оформление заказа в Telegram Mini App.
- Создание платежа LiqPay и проверка подписи callback.
- Админ-команды `/add_product`, `/delete_product`, `/orders`, `/set_status`.
- Проверка Telegram `initData` на backend.
- Бот, API и Mini App запускаются одним сервисом.

## Быстрый запуск

Нужен Python 3.11+.

```bash
git clone https://github.com/Pybackendev/bot-shop.git
cd bot-shop
python -m venv .venv
```

Активируйте окружение: PowerShell —

```powershell
.\.venv\Scripts\Activate.ps1
```

Linux/macOS:

```bash
source .venv/bin/activate
```

Установите зависимости и создайте локальный файл настроек:

```bash
pip install -r requirements.txt
```

PowerShell:

```powershell
Copy-Item .env.example .env
```

Linux/macOS:

```bash
cp .env.example .env
```

Заполните `.env`. Для запуска API и Mini App без Telegram-бота оставьте `BOT_TOKEN` пустым. Запустите из корня репозитория:

```bash
uvicorn main:app --reload
```

Mini App: http://localhost:8000/webapp/  
API: http://localhost:8000/docs

Для работы бота заполните `BOT_TOKEN` и задайте числовой `ADMIN_CHAT_ID`. Администратор может добавить товары командой `/add_product`. Оформление заказа внутри Telegram требует HTTPS и открытия Mini App из бота.

## Настройки

| Переменная | Назначение |
| --- | --- |
| `BOT_TOKEN` | Токен бота от BotFather; можно оставить пустым для локального просмотра API |
| `ADMIN_CHAT_ID` | Telegram ID администратора |
| `ADMIN_API_SECRET` | Секрет административного API |
| `RENDER_EXTERNAL_URL` | Публичный URL сервиса; нужен для ссылок Mini App и callback |
| `DATABASE_URL` | Локально по умолчанию `sqlite:///./shop.db`; на Render задаётся подключение PostgreSQL |
| `LIQPAY_PUBLIC_KEY` | Публичный ключ LiqPay |
| `LIQPAY_PRIVATE_KEY` | Приватный ключ LiqPay |

Не коммитьте `.env`, токены, ключи платежей или рабочую базу. Render Blueprint использует `requirements.txt` из корня и команду `uvicorn main:app`; `DATABASE_URL` подключается к созданной сервисом PostgreSQL.

## Структура

```text
main.py                       # FastAPI и фоновый запуск Telegram-бота
config.py                     # настройки
database.py                  # SQLAlchemy и подключение к БД
models.py / schemas.py         # модели и схемы API
api_client.py                 # вызовы backend из хендлеров
bot_start.py / bot_admin.py
router_*.py                   # маршруты API
service_*.py                  # Telegram auth, LiqPay, уведомления
webapp/                        # Mini App: HTML, CSS, JavaScript
requirements.txt               # зависимости Python
.env.example                   # шаблон переменных окружения
render.yaml                    # развёртывание на Render
```

## Автор

[Pybackendev](https://github.com/Pybackendev) · [Freelancehunt](https://freelancehunt.com/freelancer/Pybackendev.html)

