import asyncio

import httpx

from app.infra.celery_app import celery_app
from app.core.config import settings
from app.services.openrouter_client import call_openrouter


@celery_app.task(name="app.tasks.llm_tasks.llm_request")
def llm_request(tg_chat_id: int, prompt: str) -> None:
    asyncio.run(_async_llm_request(tg_chat_id, prompt))


async def _async_llm_request(tg_chat_id: int, prompt: str) -> None:
    try:
        answer = await call_openrouter(prompt)
    except Exception as e:
        answer = f"Ошибка при обращении к LLM: {e}"

    bot_url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
    async with httpx.AsyncClient(timeout=30.0) as client:
        await client.post(bot_url, json={"chat_id": tg_chat_id, "text": answer})