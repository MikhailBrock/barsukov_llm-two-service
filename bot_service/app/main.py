import asyncio

from fastapi import FastAPI

from app.bot.dispatcher import create_bot, create_dispatcher

app = FastAPI(title="Bot Service")


@app.get("/health")
async def health():
    return {"status": "ok"}


async def run_bot():
    bot = create_bot()
    dp = create_dispatcher()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(run_bot())
