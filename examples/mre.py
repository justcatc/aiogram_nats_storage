import asyncio

import nats
from aiogram import Bot, Dispatcher
from aiogram.filters.command import CommandStart
from aiogram.filters.state import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

from src.adapter import NatsAdapter
from src.storage import NatsStorage


class MainSG(StatesGroup):
    first = State()


async def start_handler(msg: Message, state: FSMContext) -> None:
    await state.set_state(MainSG.first)
    await state.set_data({"key": "value"})


async def first_state_handler(msg: Message, state: FSMContext) -> None:
    value = await state.get_state()
    data = await state.get_data()
    print(value, data)


async def main() -> None:
    bot = Bot("")

    client = await nats.connect("nats://localhost:4222")
    adapter = NatsAdapter(client=client)
    await adapter.create_kv()

    storage = NatsStorage(adapter=adapter)

    dp = Dispatcher(storage=storage)

    dp.message.register(start_handler, CommandStart())
    dp.message.register(first_state_handler, StateFilter(MainSG.first))

    try:
        await dp.start_polling(bot)
    finally:
        await storage.close()


if __name__ == "__main__":
    asyncio.run(main())
