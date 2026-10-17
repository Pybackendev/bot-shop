"""
SQLAlchemy модели для интернет-магазина в Telegram.

Product   — товар в каталоге
User      — покупатель (идентификация по telegram_id)
Order     — заказ
OrderItem — позиция в заказе (снапшот цены на момент покупки!)
"""

from datetime import datetime
import enum

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Float,
    Boolean,
    DateTime,
    ForeignKey,
    Enum,
    BigInteger,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class OrderStatus(str, enum.Enum):
    NEW = "new"                 # заказ создан, оплата не подтверждена
    PENDING_PAYMENT = "pending_payment"  # ссылка на оплату выдана, ждём вебхук
    PAID = "paid"                # оплата подтверждена (LiqPay webhook)
    PROCESSING = "processing"    # взяли в обработку
    SHIPPED = "shipped"          # отправлен
    CANCELLED = "cancelled"      # отменён


class DeliveryMethod(str, enum.Enum):
    PICKUP = "pickup"            # самовывоз
    COURIER = "courier"          # курьер
    NOVA_POSHTA = "nova_poshta"  # Новая почта


class PaymentMethod(str, enum.Enum):
    CASH = "cash"                 # наличные при получении
    CARD_ON_DELIVERY = "card_on_delivery"  # картой при получении
    LIQPAY = "liqpay"             # онлайн-оплата LiqPay


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False, index=True)
    username = Column(String(64), nullable=True)
    full_name = Column(String(128), nullable=True)
    phone = Column(String(32), nullable=True)
    is_admin = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    orders = relationship("Order", back_populates="user")


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    name = Column(String(128), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)          # текущая цена (для карточки/каталога)
    category = Column(String(64), nullable=True, index=True)
    photo_file_id = Column(String(256), nullable=True)  # Telegram file_id
    is_active = Column(Boolean, default=True, nullable=False)  # мягкое удаление
    stock = Column(Integer, default=0, nullable=False)  # остаток на складе
    created_at = Column(DateTime, default=datetime.utcnow)

    order_items = relationship("OrderItem", back_populates="product")


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # данные доставки — снапшот на момент заказа (юзер потом может их поменять в профиле)
    full_name = Column(String(128), nullable=False)
    phone = Column(String(32), nullable=False)
    address = Column(String(256), nullable=True)  # не нужен при pickup

    delivery_method = Column(Enum(DeliveryMethod), nullable=False)
    payment_method = Column(Enum(PaymentMethod), nullable=False)
    status = Column(Enum(OrderStatus), default=OrderStatus.NEW, nullable=False)

    total_amount = Column(Float, nullable=False, default=0.0)

    liqpay_order_id = Column(String(64), unique=True, nullable=True, index=True)  # order_id для LiqPay

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)

    product_name = Column(String(128), nullable=False)  # снапшот названия
    price = Column(Float, nullable=False)                # снапшот цены на момент заказа!
    quantity = Column(Integer, nullable=False, default=1)

    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")

    @property
    def subtotal(self) -> float:
        return self.price * self.quantity
