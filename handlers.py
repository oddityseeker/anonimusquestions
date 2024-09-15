from aiogram import types, Bot, F, Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.state import default_state
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
import aiosqlite
import re
import logging
import time
import text
import config
import sqlite3

logging.basicConfig(format = '[%(asctime)s | %(levelname)s]: %(message)s', datefmt='%m.%d.%Y %H:%M:%S',filename='anon.log',level=logging.DEBUG)

bot = Bot(token=config.BOT_TOKEN)
router = Router()


async def check_and_add_user(user_id: int, user_name: text):
    async with aiosqlite.connect('database.db') as db:
        # Проверка, существует ли пользователь с данным user_id
        async with db.execute("SELECT id FROM users WHERE id = ?", (user_id,)) as cursor:
            user = await cursor.fetchone()

        # Если пользователя нет, добавить его
        if user is None:
            user_name = "@" + user_name
            await db.execute("INSERT INTO users (id, username) VALUES (?, ?)", (user_id, user_name))
            await db.commit()
            print(f"Пользователь с id {user_id} добавлен в базу данных.")
        else:
            print(f"Пользователь с id {user_id} уже существует.")

# Инициализация бота и маршрутизатора

class chooser(StatesGroup):
    recipient = State()
    message_to = State()
class chooserp(StatesGroup):
    recipient = State()
    photo_to = State()

## Проверка существования пользователя
async def check_username_in_db(username):
    if username == "$гламуримеется":
      result = []
      result.append(str(config.admin))
      return result
    else:
        async with aiosqlite.connect('database.db') as db:
            cursor = await db.execute('SELECT id FROM users WHERE username = ?', (username,))
            result = await cursor.fetchone()
            return result

# Запись сообщения в текстовый файл
def log_message(sender_id, recipient_id, message_text):
    with open('messages.txt', 'a') as file:
        file.write(f"{sender_id} -> {recipient_id}, {int(time.time())}, {message_text}\n")


@router.message(StateFilter(None), Command("find"))
async def cmd_food(message: Message, state: FSMContext):
    await message.reply("Введи username для поиска")
    # Устанавливаем пользователю состояние "выбирает название"
    await state.set_state(chooser.recipient)


@router.message(StateFilter(None), Command("photo"))
async def cmd_food(message: Message, state: FSMContext):
    await message.reply("Введи username для поиска")
    # Устанавливаем пользователю состояние "выбирает название"
    await state.set_state(chooserp.recipient)


@router.message(StateFilter(None), Command("start"))
async def start_handler(msg: Message):
    await check_and_add_user(msg.from_user.id, msg.from_user.username)
    await msg.answer(text.greeting)

@router.message(StateFilter(None), Command("donate"))
async def start_handler(msg: Message):
    await msg.answer("сорян,в боте не всё реализовано, но меня можно поддержать, пока что только тоном и основаными на тоне монетами"
                     "\n\nUQBI1fJKutRxZCRXRq8hYjtyRkLyMOmwGyXOQQWtE3hreHWc")


@router.message(chooser.recipient)
async def process_username(message: types.Message, state: FSMContext):
    username = message.text.strip()  # Убираем лишние пробелы
    # Поиск username в базе данных
    result = await check_username_in_db(username)
    if result:
        global user_id
        user_id = result[0]
        await state.clear()
        await message.reply("пользователь найден\nчто хочешь спросить?")
        async with aiosqlite.connect('database.db') as db:
            await db.execute(f"UPDATE users SET recip = {user_id} WHERE id = {message.from_user.id}")
            await db.commit()

    else:
        await message.reply("Пользователь не найден.")
    # Завершаем состояние



@router.message(StateFilter(None))
async def process_username(message: types.Message, state: FSMContext,conn = sqlite3.connect("database.db")):
    message_to = message.text
    c = conn.cursor()
    c.execute( "SELECT recip FROM users WHERE id = ?", (message.from_user.id,))
    symbols_to_remove = "(,')"
    result = str(c.fetchone())
    for symbol in symbols_to_remove:
        result = result.replace(symbol, "")
    print(result)
    await bot.send_message(result, message_to)
    await bot.send_message(config.admin, f'{message.from_user.id},{str(user_id)}, {message_to}')
    log_message(message.from_user.id,user_id, message_to)
    await state.clear()


@router.message(F.photo)
async def process_username(message: types.Message, state: FSMContext,conn = sqlite3.connect("database.db")):
    id_photo = message.photo[-1].file_id
    c = conn.cursor()
    c.execute("SELECT recip FROM users WHERE id = ?", (message.from_user.id,))
    symbols_to_remove = "(,')"
    result = str(c.fetchone())
    for symbol in symbols_to_remove:
        result = result.replace(symbol, "")
    print(result)
    await bot.send_photo(result, id_photo)
    await bot.send_photo(config.admin, id_photo)
    await bot.send_message(config.admin,f'{message.from_user.id},{user_id}')
    # Завершаем состояние




