from __future__ import annotations

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.utils.markdown import hbold

from app.config.settings import settings


async def start(message: Message) -> None:
    await message.answer(f"Welcome to {hbold(settings.app_name)}!\nUse /help to see commands.")


async def help_command(message: Message) -> None:
    await message.answer("Available commands:\n/start\n/help\n/share\n/moderate")


async def share(message: Message) -> None:
    await message.answer("Share your story in the community.")


async def moderate(message: Message) -> None:
    await message.answer("Moderation queue is ready.")


def start_bot() -> None:
    if not settings.bot_token:
        raise RuntimeError("BOT_TOKEN is not configured. Set it in the environment or .env file.")

    bot = Bot(token=settings.bot_token)
    dp = Dispatcher()
    dp.message(Command("start"))(start)
    dp.message(Command("help"))(help_command)
    dp.message(Command("share"))(share)
    dp.message(Command("moderate"))(moderate)

    import asyncio
    asyncio.run(dp.start_polling(bot))
