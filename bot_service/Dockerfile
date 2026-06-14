FROM python:3.11-slim

WORKDIR /app

RUN pip install uv

COPY pyproject.toml .
RUN uv pip install --system --no-cache -r pyproject.toml 2>/dev/null || pip install fastapi uvicorn[standard] aiogram celery redis httpx pydantic-settings "python-jose[cryptography]"

COPY . .

CMD ["python", "-m", "app.main"]
