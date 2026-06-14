from aiogram import Bot, Dispatcher

from app.core.config import settings
from app.bot.handlers import router


def create_bot() -> Bot:
    return Bot(token=settings.TELEGRAM_BOT_TOKEN)


def create_dispatcher() -> Dispatcher:
    dp = Dispatcher()
    dp.include_router(router)
    return dp
