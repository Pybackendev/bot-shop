import httpx
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from .database import get_db
from .models import Product
from .schemas import ProductOut
from .config import BOT_TOKEN

router = APIRouter(prefix="/api/products", tags=["products"])


@router.get("", response_model=list[ProductOut])
def list_products(category: str | None = None, db: Session = Depends(get_db)):
    query = db.query(Product).filter(Product.is_active.is_(True))
    if category:
        query = query.filter(Product.category == category)
    return query.order_by(Product.id.desc()).all()


@router.get("/{product_id}", response_model=ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = (
        db.query(Product)
        .filter(Product.id == product_id, Product.is_active.is_(True))
        .first()
    )
    if not product:
        raise HTTPException(404, "Товар не найден")
    return product


@router.get("/{product_id}/photo")
async def get_product_photo(product_id: int, db: Session = Depends(get_db)):
    """
    Telegram file_id нельзя вставить напрямую в <img src="...">  — это не URL,
    а внутренний идентификатор. Поэтому проксируем: узнаём реальный путь файла
    через getFile и стримим байты с серверов Telegram через себя.
    Без кэша: на каждый показ картинки — один лишний запрос к Telegram API,
    для MVP это ок, при росте трафика стоит закэшировать file_path.
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product or not product.photo_file_id:
        raise HTTPException(404, "У товара нет фото")

    if not BOT_TOKEN:
        raise HTTPException(500, "BOT_TOKEN is not configured on server")

    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"https://api.telegram.org/bot{BOT_TOKEN}/getFile",
            params={"file_id": product.photo_file_id},
        )
        data = resp.json()
        if not data.get("ok"):
            raise HTTPException(502, "Не удалось получить фото из Telegram")
        file_path = data["result"]["file_path"]

        file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"
        file_resp = await client.get(file_url)
        if file_resp.status_code != 200:
            raise HTTPException(502, "Файл фото недоступен")

        content_type = file_resp.headers.get("content-type", "image/jpeg")
        return StreamingResponse(iter([file_resp.content]), media_type=content_type)
