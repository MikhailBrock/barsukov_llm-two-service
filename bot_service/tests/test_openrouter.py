import pytest
import respx
import httpx

from app.services.openrouter_client import call_openrouter
from app.core.config import settings


@pytest.mark.asyncio
@respx.mock
async def test_call_openrouter_returns_content():
    mock_response = {
        "choices": [{"message": {"content": "1828 - 1910"}}]
    }
    respx.post(f"{settings.OPENROUTER_BASE_URL}/chat/completions").mock(
        return_value=httpx.Response(200, json=mock_response)
    )

    result = await call_openrouter("Напиши годы жизни Толстого")
    assert result == "1828 - 1910"


@pytest.mark.asyncio
@respx.mock
async def test_call_openrouter_raises_on_error():
    respx.post(f"{settings.OPENROUTER_BASE_URL}/chat/completions").mock(
        return_value=httpx.Response(500, text="Internal Server Error")
    )

    with pytest.raises(RuntimeError, match="OpenRouter HTTP error"):
        await call_openrouter("test prompt")
