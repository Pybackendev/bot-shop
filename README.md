# Telegram Shop · Магазин внутри Telegram

Магазин с каталогом, корзиной и оформлением заказов в Telegram Mini App. Покупатель выбирает товары и переходит к оплате через LiqPay; администратор управляет товарами и заказами командами бота.

**Python · aiogram 3 · FastAPI · SQLAlchemy · Telegram Mini App · LiqPay**

## Возможности

- Каталог с описаниями, ценами и фотографиями товаров.
- Корзина и оформление заказа в Mini App.
- Создание ссылки на оплату LiqPay и обработка подписанного callback.
- Админ-команды `/add_product`, `/delete_product`, `/orders`, `/set_status`.
- Проверка Telegram initData на backend.
- API и бот работают в одном процессе; Mini App раздаётся как статика.
- SQLite по умолчанию; подключение PostgreSQL через `DATABASE_URL`.

## Структура репозитория

```text
main.py                    # FastAPI и фоновый запуск бота
__init__.py                # загрузка .env
config.py                  # настройки бота и URL
database.py                # SQLAlchemy и подключение БД
models.py / schemas.py     # модели данных и API
api_client.py              # вызовы backend из бота
bot_start.py / bot_admin.py # Telegram-команды
router_*.py                # HTTP-маршруты
service_*.py               # авторизация, платежи, уведомления
webapp/                    # index.html, style.css, app.js
render.yaml                # конфигурация развёртывания
```

## Локальный запуск

Нужен Python 3.11+. **Текущий код ожидает пакет `app`**: использует относительные импорты, а статика подключается по пути `app/webapp`. Поэтому клонируйте репозиторий в каталог `app` внутри рабочей папки и запускайте из родительского каталога:

```bash
mkdir telegram-shop
cd telegram-shop
git clone https://github.com/Pybackendev/bot-shop.git app
python -m venv .venv
```

Активируйте окружение: Windows PowerShell — `.\.venv\Scripts\Activate.ps1`, Linux/macOS — `source .venv/bin/activate`.

```bash
pip install -r app/requirements.txt
```

Скопируйте `app/.env.example` в `.env` **в текущей папке `telegram-shop`**, заполните настройки и запустите:

```bash
uvicorn app.main:app --reload --port 8000
```

- Mini App: http://localhost:8000/webapp/
- API-документация: http://localhost:8000/docs

Без `BOT_TOKEN` запускаются только API и Mini App. Для Telegram нужен публичный HTTPS-адрес в `RENDER_EXTERNAL_URL`. Для создания товаров отправьте `/add_product` с аккаунта, указанного в `ADMIN_CHAT_ID`. Платёжный сценарий требует ключей LiqPay и доступного callback-адреса; наличие интеграции в коде не подтверждает проведение реальных платежей.

## Переменные окружения

| Переменная | Назначение |
| --- | --- |
| `BOT_TOKEN` | Токен от BotFather |
| `ADMIN_CHAT_ID` | Числовой Telegram ID администратора |
| `ADMIN_API_SECRET` | Секрет административного API |
| `RENDER_EXTERNAL_URL` | Публичный адрес API и Mini App |
| `DATABASE_URL` | По умолчанию `sqlite:///./shop.db` |
| `LIQPAY_PUBLIC_KEY` | Публичный ключ LiqPay |
| `LIQPAY_PRIVATE_KEY` | Приватный ключ LiqPay |

Не добавляйте `.env` и рабочую базу в Git. Для развёртывания в корне checkout нужно сначала согласовать пакет `app`, путь к статике и команды в `render.yaml`. Для постоянного хранения SQLite требуется постоянный диск; альтернативный вариант — PostgreSQL. Polling-боту нужен непрерывно работающий процесс.

## Автор

[Pybackendev](https://github.com/Pybackendev) · [Связаться на Freelancehunt](https://freelancehunt.com/freelancer/Pybackendev.html)

