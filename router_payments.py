from fastapi import APIRouter, Depends, Form, HTTPException
from sqlalchemy.orm import Session

from .database import get_db
from .models import Order, OrderStatus
from .service_liqpay import verify_callback
from .service_notifications import notify_order_paid

router = APIRouter(prefix="/api/webhook", tags=["payments"])


@router.post("/payment")
async def liqpay_webhook(
    data: str = Form(...),
    signature: str = Form(...),
    db: Session = Depends(get_db),
):
    try:
        payload = verify_callback(data, signature)
    except ValueError:
        # Подпись не сошлась — не доверяем запросу. 400, а не 401/403,
        # так и не даём никакой подсказки о том, что именно не так.
        raise HTTPException(400, "invalid signature")

    if payload.get("status") not in ("success", "sandbox"):
        # платёж не прошёл (failure, reversed и т.д.) — просто игнорируем,
        # заказ останется в pending_payment
        return {"ok": True}

    order = db.query(Order).filter(Order.liqpay_order_id == payload["order_id"]).first()
    if not order:
        raise HTTPException(404, "order not found")

    if order.status != OrderStatus.PAID:
        order.status = OrderStatus.PAID
        db.commit()
        await notify_order_paid(order)

    return {"ok": True}
