import asyncio
import json
import logging
import sys

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, URLInputFile, ReplyKeyboardRemove, InlineKeyboardButton

from conf import BOT_TOKEN, ADMI_ID
from commands import (GAME_BOT_COMMAND, GAME_BOT_CREATE_COMMAND,
                      GAME_COMMAND, GAME_CREATE_COMMAND,
                      HELP_COMMAND, HELP)
from keyborts import games_keyboard_markup, GameCallback, GameRating
from  models import Game
from state import GameForm, GameRating

# Bot token can be obtained via https://t.me/BotFather
TOKEN = BOT_TOKEN

# All handlers should be attached to the Router (or Dispatcher)

dp = Dispatcher()
@dp.message(HELP_COMMAND)
async def help(message: Message) -> None:
    await message.answer(f"{html.code(message.from_user.full_name)} ти тут зможеж отримати інформацію про ігри, і оцінити їх.")

@dp.message(Command("info"))
async def info(message: Message) -> None:
    await message.answer(f"Hello, {html.bold(message.from_user.id)}!")

@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    This handler receives messages with `/start` command
    """
    # Most event objects have aliases for API methods that can be called in events' context
    # For example if you want to answer to incoming message you can use `message.answer(...)` alias
    # and the target chat will be passed to :ref:`aiogram.methods.send_message.SendMessage`
    # method automatically or call API method directly via
    # Bot instance: `bot.send_message(chat_id=message.chat.id, ...)`
    await message.answer(f"Hello, {html.code(message.from_user.full_name)}!")
    logging.info(f"{html.link(message.from_user.full_name)} has started")

@dp.message(Command("who_developer"))
async def link(message: Message) -> None:
    """
        This handler receives messages with `/start` command
        """
    # Most event objects have aliases for API methods that can be called in events' context
    # For example if you want to answer to incoming message you can use `message.answer(...)` alias
    # and the target chat will be passed to :ref:`aiogram.methods.send_message.SendMessage`
    # method automatically or call API method directly via
    # Bot instance: `bot.send_message(chat_id=message.chat.id, ...)`
    await message.answer(f"{html.code(message.from_user.full_name)}, don't you know?! That's Yaroslav Bilovsky!")

def get_game(file_path: str = "data.json", game_id: int | None = None):
    with open(file_path, "r", encoding="utf-8") as fp:
        games = json.load(fp)
        if game_id != None and game_id < len(games):
            return games[game_id]
        return games

def add_game(game: dict, file_path: str = "data.json"):
    games = get_game()
    if games:
        games.append(game)
        with open(file_path, "w", encoding="utf-8") as fp:
            json.dump(
                games,
                fp,
                indent=4,
                ensure_ascii=False
            )


@dp.message(GAME_COMMAND)
async def games(message: Message) -> None:
    data = get_game()
    markup = games_keyboard_markup(game_list=data)
    await message.answer(f"Список ігор. Натисніть назву для деталей",
                            reply_markup=markup)

async def main() -> None:
    # Initialize Bot instance with default bot properties which will be passed to all API calls
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    await  bot.set_my_commands(
        [
            GAME_BOT_COMMAND,
            GAME_BOT_CREATE_COMMAND,
            HELP
        ]
    )

    # And the run events dispatching
    await dp.start_polling(bot)

@dp.callback_query(GameCallback.filter())
async def callback_game(callback: CallbackQuery, callback_data: GameCallback, state: FSMContext, **kwargs) -> None:
    print('state', state)
    print('callback_game')
    print(callback)
    print()
    print(callback_data)
    print('kwargs', kwargs)
    if callback_data.button == "game_selector":
        await game_selekt(callback, callback_data)
    elif callback_data.button == "rating":
        await game_to_evaluate(callback, callback_data, state)

async def game_selekt(callback: CallbackQuery, callback_data: GameCallback):
    game_id = callback_data.id
    game_data = get_game(game_id=game_id)
    game = Game(**game_data)
    text = f"Гра: {game.name}\n" \
           f"Опис: {game.description}\n" \
           f"Рейтинг: {game.rating}\n" \
           f"Жанр: {game.genre}\n" \
           f"Автори: {','.join(game.authors)}\n"
    keyboard = []
    keyboard.append(
        [

            InlineKeyboardButton(
                text="Оцінити гру",
                callback_data=GameCallback(id=game_id, button="rating").pack()

            )

        ]
    )
    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)

    try:
        await callback.message.answer_photo(
            photo=URLInputFile(
                game.poster,
                filename=f"{game.name}_cover.{game.poster.split('.')[-1]}"
            )
        )

        await callback.message.answer(text, reply_markup=markup)

    except Exception as e:
        await callback.message.answer(text)
        logging.error(logging.error(f"Failed to load images for game{game.name}: {str(e)}"))

async def game_to_evaluate(callback: CallbackQuery, callback_data: GameCallback, state: FSMContext)   -> None:
     print('state', state)
     game_id = callback_data.id
     print('game_to_evaluate')
     print('rating', callback)
     print('game_id', game_id)
     data = await state.update_data(game_id=game_id)
     await state.set_state(GameRating.rating)
     await callback.answer(f"Введіть оціну від 1 до 10.",
                         reply_markup=ReplyKeyboardRemove())


@dp.message(GameRating.rating)
async def game_to_evaluate_state_2(message: Message, state: FSMContext) -> None:
    print('message', message.text, message)
    data = await state.get_data()
    print('state', state, data)
    game_id = data['game_id']
    rating = message.text
    # game_id = callback_data.id
    # print('game_id', game_id)
    # game_data = get_game(game_id=game_id)
    # print('game_data', game_data)

    # game = Game(**game_data)
    # await state.update_data(name=game.name)
    # await state.update_data(description=game.description)
    # await state.update_data(rating=message.text)
    # await state.update_data(genre=game.genre)
    # await state.update_data(authors=','.join(game.authors))
    # data = await state.update_data(poster=game.poster)
    # game2 = Game(**data)
    try:
        print(game_id)
        if int(rating) > 0 and int(rating) < 11:
            with open("data.json", "r", encoding="utf-8") as fp:
                games = json.load(fp)
                game_data = games[game_id]
                do_rating = game_data['rating']
                pisla_rating = (int(do_rating) + int(rating)) / 2
            with open("data.json", "w", encoding="utf-8") as fp:
                game_data["rating"] = pisla_rating
                print(game_data)
                json.dump(games, fp, indent=4, ensure_ascii=False)
                await state.clear()
        else:
            await CallbackQuery.message.answer("Від 1 до 10! Не більше не менше!")
    except ValueError:
        await CallbackQuery.message.answer("Це не число!")






@dp.message(GAME_CREATE_COMMAND)
async def game_create(message: Message, state: FSMContext) -> None:
    if message.from_user.id == int(ADMI_ID):
        await state.set_state(GameForm.name)
        await message.answer(f"Введіть назву гри",
                         reply_markup=ReplyKeyboardRemove())
    else:
        await message.answer(f"Тльки адмін це може зробити!")

@dp.message(GameForm.name)
async def game_name(message: Message, state: FSMContext) -> None:
    await state.update_data(name=message.text)
    await state.set_state(GameForm.description)
    await message.answer(f"Введіть опис гри",
                         reply_markup=ReplyKeyboardRemove())

@dp.message(GameForm.description)
async def game_description(message: Message, state: FSMContext) -> None:
    await state.update_data(description=message.text)
    await state.set_state(GameForm.rating)
    await message.answer(f"Введіть рейтинг гри від 1 до 10",
                         reply_markup=ReplyKeyboardRemove())

@dp.message(GameForm.rating)
async def game_rating(message: Message, state: FSMContext) -> None:
    await state.update_data(rating=message.text)
    await state.set_state(GameForm.genre)
    await message.answer(f"Введіть жанр гри",
                         reply_markup=ReplyKeyboardRemove())

@dp.message(GameForm.genre)
async def game_genre(message: Message, state: FSMContext) -> None:
    await state.update_data(genre=message.text)
    await state.set_state(GameForm.authors)
    await message.answer(f"Введіть авторів гри.\n" +
                         html.bold("Обов'яскова кома та відступ після неї"),
                         reply_markup=ReplyKeyboardRemove())

@dp.message(GameForm.authors)
async def game_authors(message: Message, state: FSMContext) -> None:
    await state.update_data(authors=[x for x in message.text.split(", ")])
    await state.set_state(GameForm.poster)
    await message.answer(f"Введіть посилання на картинку гри.",
                         reply_markup=ReplyKeyboardRemove())

@dp.message(GameForm.poster)
async def game_poster(message: Message, state: FSMContext) -> None:
   data = await state.update_data(poster=message.text)
   game = Game(**data)
   add_game(game.model_dump())
   await state.clear()
   await message.answer(f"Гру {game.name} успішно додано",
                        reply_markup=ReplyKeyboardRemove())




if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
