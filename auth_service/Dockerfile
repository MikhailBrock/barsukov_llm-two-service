FROM python:3.11-slim

WORKDIR /app

RUN pip install uv

COPY pyproject.toml .
RUN uv pip install --system --no-cache -r pyproject.toml 2>/dev/null || pip install fastapi uvicorn[standard] sqlalchemy aiosqlite "pydantic[email]" pydantic-settings "python-jose[cryptography]" "passlib[bcrypt]" python-multipart greenlet "bcrypt==4.3.0"

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
