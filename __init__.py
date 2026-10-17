from dotenv import load_dotenv

# Грузим .env здесь, а не в config.py: это выполняется раньше любого
# submodule-импорта внутри пакета (telegram_auth.py, liqpay_service.py,
# notifications.py читают os.getenv() сами на уровне модуля, и если бы
# .env подгружался позже — их значения остались бы пустыми).
load_dotenv()
