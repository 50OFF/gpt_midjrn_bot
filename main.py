import openai
import asyncio
import logging
import sys
import config as cfg
import database as db

from aiogram import Bot, Dispatcher, Router, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.filters.command import Command
from aiogram.filters.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext

openai.api_key = cfg.CHATGPT_KEY
TOKEN = cfg.BOT_TOKEN

storage = MemoryStorage()
dp = Dispatcher(storage=storage)


@dp.message()
async def response(message: Message):
    db.Database.c.execute("SELECT * FROM user_info WHERE user_id = ?", (message.from_user.id, ))
    if len(db.Database.c.fetchall()) == 0:
        db.Database.add_user(message.from_user.id, "today")
    db.Database.add_message(message.from_user.id, message.text, "user")
    resp = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=db.Database.get_history(message.from_user.id)
    )
    resp_text = resp.choices[0]["message"]["content"]
    tokens = resp.usage["total_tokens"]
    print(resp.usage["prompt_tokens"])
    print(resp.usage["completion_tokens"])
    await message.answer(resp.choices[0]["message"]["content"])
    db.Database.add_message(message.from_user.id, resp_text, "assistant")
    db.Database.add_tokens(message.from_user.id, tokens)


async def main() -> None:
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
