import asyncio
import logging

from aiogram import Bot, Dispatcher

from app.bot.handlers import build_router
from app.config import get_settings


async def run_bot() -> None:
    token = get_settings().telegram_bot_token
    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not configured")
    bot = Bot(token=token)
    dispatcher = Dispatcher()
    dispatcher.include_router(build_router())
    try:
        await dispatcher.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(run_bot())
