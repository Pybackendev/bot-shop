from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

from config import ADMIN_CHAT_ID
import api_client

router = Router()


def is_admin(message: Message) -> bool:
    return message.from_user.id == ADMIN_CHAT_ID


class AddProduct(StatesGroup):
    name = State()
    description = State()
    price = State()
    photo = State()


@router.message(Command("add_product"), F.func(is_admin))
async def add_product_start(message: Message, state: FSMContext):
    await state.set_state(AddProduct.name)
    await message.answer("Название товара?")


@router.message(AddProduct.name)
async def add_product_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(AddProduct.description)
    await message.answer("Описание товара?")


@router.message(AddProduct.description)
async def add_product_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await state.set_state(AddProduct.price)
    await message.answer("Цена (число, например 350.0)?")


@router.message(AddProduct.price)
async def add_product_price(message: Message, state: FSMContext):
    try:
        price = float(message.text.replace(",", "."))
    except ValueError:
        await message.answer("Похоже, это не число. Попробуй ещё раз, например: 350.0")
        return
    await state.update_data(price=price)
    await state.set_state(AddProduct.photo)
    await message.answer("Пришли фото товара (или напиши /skip, чтобы без фото)")


@router.message(AddProduct.photo, F.photo)
async def add_product_photo(message: Message, state: FSMContext):
    photo_file_id = message.photo[-1].file_id
    await _finish_add_product(message, state, photo_file_id)


@router.message(AddProduct.photo, Command("skip"))
async def add_product_skip_photo(message: Message, state: FSMContext):
    await _finish_add_product(message, state, None)


async def _finish_add_product(message: Message, state: FSMContext, photo_file_id: str | None):
    data = await state.get_data()
    try:
        product = await api_client.add_product(
            name=data["name"],
            description=data["description"],
            price=data["price"],
            photo_file_id=photo_file_id,
        )
        await message.answer(f"✅ Товар «{product['name']}» добавлен (id={product['id']})")
    except Exception as e:
        await message.answer(f"❌ Не удалось добавить товар: {e}")
    finally:
        await state.clear()


@router.message(Command("delete_product"), F.func(is_admin))
async def delete_product_cmd(message: Message):
    parts = message.text.split()
    if len(parts) != 2 or not parts[1].isdigit():
        await message.answer("Использование: /delete_product <id>")
        return
    product_id = int(parts[1])
    try:
        await api_client.delete_product(product_id)
        await message.answer(f"🗑 Товар id={product_id} удалён (скрыт из каталога)")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")


@router.message(Command("orders"), F.func(is_admin))
async def list_orders_cmd(message: Message):
    orders = await api_client.list_orders()
    if not orders:
        await message.answer("Заказов пока нет")
        return
    lines = [
        f"#{o['id']} — {o['status']} — {o['total_amount']} грн" for o in orders
    ]
    await message.answer("\n".join(lines))


@router.message(Command("set_status"), F.func(is_admin))
async def set_status_cmd(message: Message):
    parts = message.text.split()
    if len(parts) != 3 or not parts[1].isdigit():
        await message.answer("Использование: /set_status <order_id> <new|processing|shipped|cancelled>")
        return
    order_id, status = int(parts[1]), parts[2]
    try:
        await api_client.update_order_status(order_id, status)
        await message.answer(f"✅ Статус заказа #{order_id} → {status}")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")
