# Telegram Shop Bot — один сервис

Бот (aiogram 3, polling) + FastAPI backend + Mini App — всё в одном процессе,
один Render Web Service (бесплатный тариф).

## Как это работает

- Бот запускается фоновой задачей внутри того же процесса, что и FastAPI
  (`app/main.py`, `lifespan`) — отдельный воркер/сервис не нужен.
- Mini App отдаётся тем же сервисом статикой по пути `/webapp`.
- API живёт по `/api/...` на том же домене — Mini App ходит на `window.location.origin`.
- Бот-админка (`/add_product`, `/orders` и т.д.) зовёт функции backend
  напрямую (`app/api_client.py`), без HTTP — один процесс, один SQLite-файл.

## Локальный запуск

```bash
pip install -r requirements.txt
cp .env.example .env  # заполнить BOT_TOKEN, ADMIN_CHAT_ID и т.д.
uvicorn app.main:app --reload --port 8000
```

Открой `http://localhost:8000/webapp` в браузере — каталог должен подгрузиться
(добавь товар через `/add_product` в личке с ботом). Для теста прямо внутри
Telegram нужен HTTPS — либо деплой на Render, либо `ngrok http 8000`
и `RENDER_EXTERNAL_URL=https://<ngrok-адрес>` в `.env`.

## Деплой на Render

1. Залить репозиторий на GitHub.
2. Render → New → Blueprint → указать репозиторий (подхватит `render.yaml`),
   либо руками: New → Web Service, `pip install -r requirements.txt`,
   старт-команда `uvicorn app.main:app --host 0.0.0.0 --port $PORT`.
3. В Environment проставить `BOT_TOKEN`, `ADMIN_CHAT_ID`, `ADMIN_API_SECRET`,
   `LIQPAY_PUBLIC_KEY`, `LIQPAY_PRIVATE_KEY`.
4. `RENDER_EXTERNAL_URL` можно не задавать вручную — Render сам прокидывает
   похожую переменную (`RENDER_EXTERNAL_URL`) для сервисов на своём домене;
   если не появится сама, впиши финальный `https://<имя>.onrender.com` руками.

⚠️ **Free-тариф Render "усыпляет" сервис без трафика** — бот на polling в
это время не будет отвечать. Для постоянно живого бота нужен платный план
или внешний пинг (например, UptimeRobot дергает `/` раз в 10 минут).

⚠️ **SQLite на Render — не персистентный.** Файл `shop.db` слетит при любом
редеплое/рестарте. Для демо/портфолио ок, для реального магазина — нужен
Render Disk (платный) либо переезд на управляемую БД.

## Структура

```
app/
├── main.py            # FastAPI + бот в одном процессе + отдача Mini App
├── config.py           # токены, URL
├── database.py          # SQLite/SQLAlchemy сессии
├── models.py            # Product, Order, OrderItem, User
├── schemas.py            # Pydantic-схемы
├── api_client.py          # прямые вызовы backend-логики из бота (без HTTP)
├── routers/              # products, orders, payments (webhook), admin
├── services/              # telegram_auth (валидация initData), liqpay, notifications
├── bot_handlers/            # /start, админ-команды
└── webapp/                   # Mini App: index.html, style.css, app.js
```

## Что дальше не сделано

- Рендер фото товара в Mini App (photo_file_id нужно отдавать через
  Telegram File API или хранить в облаке)
- Пагинация/поиск каталога, "Мои заказы"
- Тесты
