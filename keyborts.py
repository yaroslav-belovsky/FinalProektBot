from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters.callback_data import CallbackData

class GameCallback(CallbackData,prefix="games"):
    id: int
    button: str

class GameRating(CallbackData,prefix="games"):
    id: int

def games_keyboard_markup(game_list:list[dict])->InlineKeyboardMarkup:
    keyboard =[]

    for i, game in enumerate(game_list):
        keyboard.append(
            [

                InlineKeyboardButton(
                    text=game["name"],
                    callback_data=GameCallback(id=i, button='game_selector').pack()

                )

            ]
        )
    return  InlineKeyboardMarkup(inline_keyboard=keyboard)
def games_keyboard_markup_rating(game_list:list[dict])->InlineKeyboardMarkup:
    keyboard =[]

    for i, game in enumerate(game_list):
        keyboard.append(
            [

                InlineKeyboardButton(
                    text=game["name"],
                    callback_data=GameCallback(id=i).pack()

                )

            ]
        )
    return  InlineKeyboardMarkup(inline_keyboard=keyboard)