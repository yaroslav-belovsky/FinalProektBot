from aiogram.fsm.state import State, StatesGroup

class GameForm(StatesGroup):
    name = State()
    description = State()
    rating = State()
    genre = State()
    authors = State()
    poster = State()