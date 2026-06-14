import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone, timedelta

from jose import jwt

from app.core.config import settings


def make_token(sub: str = "1", role: str = "user") -> str:
    now = datetime.now(timezone.utc)
    exp = now + timedelta(hours=1)
    payload = {"sub": sub, "role": role, "iat": int(now.timestamp()), "exp": int(exp.timestamp())}
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALG)


def make_message(text: str, user_id: int = 123, chat_id: int = 456) -> MagicMock:
    msg = MagicMock()
    msg.text = text
    msg.from_user = MagicMock()
    msg.from_user.id = user_id
    msg.chat = MagicMock()
    msg.chat.id = chat_id
    msg.answer = AsyncMock()
    return msg


@pytest.mark.asyncio
async def test_token_command_saves_to_redis(fake_redis):
    from app.bot.handlers import cmd_token
    token = make_token()
    msg = make_message(f"/token {token}")

    with patch("app.bot.handlers.get_redis", return_value=AsyncMock(return_value=fake_redis)) as mock_get:
        mock_get.return_value = fake_redis
        with patch("app.bot.handlers.get_redis", new=AsyncMock(return_value=fake_redis)):
            await cmd_token(msg)

    saved = await fake_redis.get(f"token:{msg.from_user.id}")
    assert saved == token
    msg.answer.assert_called_once()
    assert "сохранён" in msg.answer.call_args[0][0]


@pytest.mark.asyncio
async def test_handle_text_no_token(fake_redis):
    from app.bot.handlers import handle_text

    msg = make_message("Привет")
    with patch("app.bot.handlers.get_redis", new=AsyncMock(return_value=fake_redis)):
        await handle_text(msg)

    msg.answer.assert_called_once()
    assert "Токен не найден" in msg.answer.call_args[0][0]


@pytest.mark.asyncio
async def test_handle_text_with_token_calls_celery(fake_redis):
    from app.bot.handlers import handle_text

    token = make_token()
    await fake_redis.set(f"token:123", token)

    msg = make_message("Вопрос к LLM", user_id=123)

    with patch("app.bot.handlers.get_redis", new=AsyncMock(return_value=fake_redis)):
        with patch("app.bot.handlers.llm_request") as mock_task:
            mock_task.delay = MagicMock()
            await handle_text(msg)
            mock_task.delay.assert_called_once_with(msg.chat.id, msg.text)

    assert "Запрос принят" in msg.answer.call_args_list[0][0][0]
