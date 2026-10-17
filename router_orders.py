import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import Product, Order, OrderItem, User, PaymentMethod, OrderStatus
from schemas import OrderCreate, OrderOut
from service_telegram_auth import get_telegram_user
from service_liqpay import create_payment_link
from service_notifications import notify_order_created

router = APIRouter(prefix="/api/order", tags=["orders"])


def _get_or_create_user(db: Session, tg_user: dict) -> User:
    user = db.query(User).filter(User.telegram_id == tg_user["telegram_id"]).first()
    if not user:
        user = User(
            telegram_id=tg_user["telegram_id"],
            username=tg_user.get("username"),
            full_name=tg_user.get("full_name"),
        )
        db.add(user)
        db.flush()
    return user


@router.post("", response_model=OrderOut)
async def create_order(
    payload: OrderCreate,
    db: Session = Depends(get_db),
    tg_user: dict = Depends(get_telegram_user),
):
    if not payload.items:
        raise HTTPException(400, "Корзина пуста")

    user = _get_or_create_user(db, tg_user)

    order = Order(
        user_id=user.id,
        full_name=payload.full_name,
        phone=payload.phone,
        address=payload.address,
        delivery_method=payload.delivery_method,
        payment_method=payload.payment_method,
        status=OrderStatus.NEW,
    )
    db.add(order)
    db.flush()  # получаем order.id, ещё не коммитим

    total = 0.0
    for item in payload.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if not product or not product.is_active:
            raise HTTPException(400, f"Товар {item.product_id} недоступен")
        if product.stock < item.quantity:
            raise HTTPException(400, f"Недостаточно товара «{product.name}» на складе")

        # снапшот цены и названия — важно, чтобы старые заказы не пересчитывались
        # задним числом при изменении цены товара
        order_item = OrderItem(
            order_id=order.id,
            product_id=product.id,
            product_name=product.name,
            price=product.price,
            quantity=item.quantity,
        )
        db.add(order_item)
        product.stock -= item.quantity
        total += product.price * item.quantity

    order.total_amount = total

    payment_url = None
    if payload.payment_method == PaymentMethod.LIQPAY:
        order.liqpay_order_id = f"order_{order.id}_{uuid.uuid4().hex[:8]}"
        order.status = OrderStatus.PENDING_PAYMENT
        payment_url = create_payment_link(order.liqpay_order_id, total, f"Заказ #{order.id}")

    db.commit()
    db.refresh(order)

    if payload.payment_method != PaymentMethod.LIQPAY:
        await notify_order_created(order)

    result = OrderOut.model_validate(order)
    result.payment_url = payment_url
    return result
