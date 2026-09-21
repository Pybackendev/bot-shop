from typing import Optional
from pydantic import BaseModel, Field

from .models import DeliveryMethod, PaymentMethod, OrderStatus


# ---------- Product ----------

class ProductOut(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    price: float
    category: Optional[str] = None
    photo_file_id: Optional[str] = None
    stock: int

    class Config:
        from_attributes = True


class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    category: Optional[str] = None
    photo_file_id: Optional[str] = None
    stock: int = 0


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    category: Optional[str] = None
    photo_file_id: Optional[str] = None
    stock: Optional[int] = None
    is_active: Optional[bool] = None


# ---------- Order ----------

class OrderItemIn(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)


class OrderCreate(BaseModel):
    # initData передаём отдельно в заголовке, тут — сами данные заказа
    full_name: str
    phone: str
    address: Optional[str] = None
    delivery_method: DeliveryMethod
    payment_method: PaymentMethod
    items: list[OrderItemIn]


class OrderItemOut(BaseModel):
    product_name: str
    price: float
    quantity: int
    subtotal: float

    class Config:
        from_attributes = True


class OrderOut(BaseModel):
    id: int
    status: OrderStatus
    total_amount: float
    delivery_method: DeliveryMethod
    payment_method: PaymentMethod
    items: list[OrderItemOut]
    payment_url: Optional[str] = None  # заполняется, если payment_method == liqpay

    class Config:
        from_attributes = True
