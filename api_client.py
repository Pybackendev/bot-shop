"""
Раньше бот и backend были разными процессами и общались по HTTP.
Теперь всё в одном процессе (один Render-сервис) — можно звать
функции backend напрямую, без похода по сети. Сигнатуры оставил
такими же, чтобы bot_handlers не пришлось переписывать.
"""

from .database import SessionLocal
from .models import Product, Order, OrderStatus


async def add_product(name: str, description: str, price: float, photo_file_id: str | None, stock: int = 0) -> dict:
    db = SessionLocal()
    try:
        product = Product(
            name=name, description=description, price=price,
            photo_file_id=photo_file_id, stock=stock,
        )
        db.add(product)
        db.commit()
        db.refresh(product)
        return {"id": product.id, "name": product.name}
    finally:
        db.close()


async def delete_product(product_id: int) -> None:
    db = SessionLocal()
    try:
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise ValueError("Товар не найден")
        product.is_active = False
        db.commit()
    finally:
        db.close()


async def list_orders() -> list[dict]:
    db = SessionLocal()
    try:
        orders = db.query(Order).order_by(Order.id.desc()).limit(50).all()
        return [
            {"id": o.id, "status": o.status.value, "total_amount": o.total_amount}
            for o in orders
        ]
    finally:
        db.close()


async def update_order_status(order_id: int, status: str) -> None:
    db = SessionLocal()
    try:
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise ValueError("Заказ не найден")
        try:
            order.status = OrderStatus(status)
        except ValueError:
            valid = ", ".join(s.value for s in OrderStatus)
            raise ValueError(f"неверный статус, допустимые: {valid}")
        db.commit()
    finally:
        db.close()
