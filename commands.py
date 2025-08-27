from aiogram.filters import Command
from aiogram.types.bot_command import BotCommand

HELP = BotCommand(command="help", description="допомога")
GAME_BOT_COMMAND = BotCommand(command="game", description="Показати список ігор")
GAME_BOT_CREATE_COMMAND = BotCommand(command="add_game", description="Додати гру")

HELP_COMMAND = Command("help")
GAME_COMMAND = Command("game")
GAME_CREATE_COMMAND = Command("add_game")
