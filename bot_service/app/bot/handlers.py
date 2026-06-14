from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.core.jwt import decode_and_validate
from app.infra.redis import get_redis
from app.tasks.llm_tasks import llm_request

router = Router()


def _redis_key(tg_user_id: int) -> str:
    return f"token:{tg_user_id}"


@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "Это бот с доступом к большой языковой модели по JWT-токену.\n"
        "Сначала отправьте токен командой: /token <JWT>\n"
        "Потом просто напишите вопрос и я с удовольствием вам отвечу!"
    )


@router.message(Command("token"))
async def cmd_token(message: Message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2 or not parts[1].strip():
        await message.answer("Использование: /token <JWT>")
        return

    token = parts[1].strip()
    try:
        decode_and_validate(token)
    except ValueError as e:
        await message.answer(f"Токен недействителен: {e}")
        return

    redis = await get_redis()
    await redis.set(_redis_key(message.from_user.id), token)
    await message.answer("Токен сохранён. Теперь можно отправлять запросы модели.")


@router.message()
async def handle_text(message: Message):
    redis = await get_redis()
    token = await redis.get(_redis_key(message.from_user.id))

    if not token:
        await message.answer(
            "Токен не найден. Пожалуйста, авторизуйтесь через Auth Service и передайте токен командой /token <JWT>."
        )
        return

    try:
        decode_and_validate(token)
    except ValueError as e:
        await message.answer(f"Токен недействителен или истёк: {e}. Получите новый токен и передайте командой /token <JWT>.")
        return

    await message.answer("Запрос принят. Ответ придёт следующим сообщением.")
    llm_request.delay(message.chat.id, message.text)
