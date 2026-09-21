import os

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from .database import get_db
from .models import Product, Order, OrderStatus
from .schemas import ProductCreate, ProductUpdate, ProductOut, OrderOut

router = APIRouter(prefix="/api/admin", tags=["admin"])

# Простой секрет между ботом и бэкендом — не путать с оплатой пользователей.
# Бот шлёт этот заголовок при каждом админ-запросе, чтобы левый человек,
# даже зная адрес API, не мог редактировать каталог.
ADMIN_API_SECRET = os.getenv("ADMIN_API_SECRET", "")


def check_admin_secret(x_admin_secret: str = Header(..., alias="X-Admin-Secret")):
    if not ADMIN_API_SECRET or x_admin_secret != ADMIN_API_SECRET:
        raise HTTPException(403, "forbidden")


@router.post("/products", response_model=ProductOut, dependencies=[Depends(check_admin_secret)])
def create_product(payload: ProductCreate, db: Session = Depends(get_db)):
    product = Product(**payload.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@router.patch("/products/{product_id}", response_model=ProductOut, dependencies=[Depends(check_admin_secret)])
def update_product(product_id: int, payload: ProductUpdate, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(404, "Товар не найден")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(product, field, value)
    db.commit()
    db.refresh(product)
    return product


@router.delete("/products/{product_id}", dependencies=[Depends(check_admin_secret)])
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(404, "Товар не найден")
    # мягкое удаление — чтобы не сломать историю старых заказов (OrderItem
    # хранит свой снапшот, но product_id всё равно ссылается на товар)
    product.is_active = False
    db.commit()
    return {"ok": True}


@router.get("/orders", response_model=list[OrderOut], dependencies=[Depends(check_admin_secret)])
def list_orders(db: Session = Depends(get_db)):
    return db.query(Order).order_by(Order.id.desc()).limit(50).all()


@router.patch("/orders/{order_id}/status", dependencies=[Depends(check_admin_secret)])
def update_order_status(order_id: int, status: str, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(404, "Заказ не найден")
    try:
        order.status = OrderStatus(status)
    except ValueError:
        valid = ", ".join(s.value for s in OrderStatus)
        raise HTTPException(400, f"Неверный статус. Допустимые значения: {valid}")
    db.commit()
    return {"ok": True}
