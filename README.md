# Двухсервисная система LLM-консультаций

## Архитектура

Система состоит из двух независимых сервисов:

```
┌─────────────────────┐     JWT      ┌──────────────────────────┐
│    Auth Service     │ ──────────▶  │      Bot Service         │
│  (FastAPI, :8000)   │              │  (aiogram + Celery)      │
│                     │              │                          │
│ POST /auth/register │              │  /token <JWT>  →  Redis  │
│ POST /auth/login    │              │  text msg      →  RabbitMQ│
│ GET  /auth/me       │              │                          │
└─────────────────────┘              └──────────────────────────┘
         │                                        │
         │ SQLite                      ┌──────────┴──────────┐
         ▼                             ▼                     ▼
    [users DB]                    [RabbitMQ]             [Redis]
                                  (broker)          (JWT store / backend)
                                       │
                                       ▼
                                [Celery Worker]
                                       │
                                       ▼
                                 [OpenRouter LLM]
```

### Auth Service
- FastAPI-приложение на порту 8000
- Хранит пользователей в SQLite
- Выдаёт JWT с полями `sub`, `role`, `iat`, `exp`
- Swagger: http://localhost:8000/docs

### Bot Service
- Telegram-бот на aiogram 3
- Валидирует JWT локально (общий `JWT_SECRET`)
- Токен привязывается к `tg_user_id` в Redis
- Запросы к LLM отправляются через Celery - RabbitMQ - Worker

## Запуск

### Требования
- Docker & Docker Compose
- Заполнить `bot_service/.env`: `TELEGRAM_BOT_TOKEN` и `OPENROUTER_API_KEY`

```bash
docker-compose up --build
```

### Swagger Auth Service
Открыть http://localhost:8000/docs

### RabbitMQ Management
Открыть http://localhost:15672 

## Пользовательский сценарий

1. Зарегистрироваться через Swagger: `POST /auth/register` с `{"email": "barsukov@email.com", "password": "password123"}`
2. Войти: `POST /auth/login` - получить JWT
3. Передать токен боту: `/token <JWT>`
4. Задать вопрос - бот отправит задачу в RabbitMQ, Celery Worker обратится к LLM и пришлёт ответ

## Тесты

### Auth Service
```bash
cd auth_service
uv run pytest tests/ -v
```

### Bot Service
```bash
cd bot_service
uv run pytest tests/ -v
```

## Структура проекта

```
project/
├── docker-compose.yml
├── screenshots/
│   ├── 01_auth_register.jpeg
│   ├── 02_auth_login.jpeg
│   ├── 03_auth_me.jpeg
│   ├── 04_telegram_bot.jpeg
│   ├── 05_rabbitmq.jpeg
│   ├── 06_auth_tests.jpeg
│   └── 07_bot_tests.jpeg
├── auth_service/
│   ├── app/
│   │   ├── main.py
│   │   ├── core/        # config, security, exceptions
│   │   ├── db/          # base, session, models
│   │   ├── schemas/     # auth, user
│   │   ├── repositories/
│   │   ├── usecases/
│   │   └── api/         # deps, routes, router
│   ├── tests/
│   ├── pyproject.toml
│   ├── pytest.ini
│   └── .env
└── bot_service/
    ├── app/
    │   ├── main.py
    │   ├── core/        # config, jwt
    │   ├── infra/       # redis, celery_app
    │   ├── tasks/       # llm_tasks
    │   ├── services/    # openrouter_client
    │   └── bot/         # dispatcher, handlers
    ├── tests/
    ├── pyproject.toml
    ├── pytest.ini
    └── .env
```
## Скриншоты

- Регистрация пользователя в Auth Service - `screenshots/01_auth_register.jpeg`
- Логин и выдача JWT - `screenshots/02_auth_login.jpeg`
- /auth/me по валидному токену - `screenshots/03_auth_me.jpeg`
- Пример диалога с ботом - `screenshots/04_telegram_bot.jpeg`
- Интерфейс RabbitMQ с очередью - `screenshots/05_rabbitmq.jpeg`
- Запуск тестов Auth Service - `screenshots/06_auth_tests.jpeg`
- Запуск тестов Bot Service - `screenshots/07_bot_tests.jpeg`
