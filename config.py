import os
# .env уже подгружен в app/__init__.py до этого импорта — здесь просто читаем.

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID", "0"))

# На Render сервис живёт на одном домене — Mini App отдаём тем же
# процессом по пути /webapp, поэтому URL строим от своего же адреса.
RENDER_EXTERNAL_URL = os.getenv("RENDER_EXTERNAL_URL", "http://localhost:8000")
WEBAPP_URL = f"{RENDER_EXTERNAL_URL}/webapp/"

ADMIN_API_SECRET = os.getenv("ADMIN_API_SECRET", "")
