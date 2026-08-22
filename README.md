# EventScout KZ

ИИ-агрегатор событий Казахстана: хакатонов, соревнований по робототехнике, стартап-мероприятий, game jam и встреч по cybersecurity.

## Возможности

- FastAPI API с фильтрацией событий по городу и категории.
- SQLAlchemy-модель, SQLite по умолчанию, готовность к PostgreSQL через `DATABASE_URL`.
- Alembic-миграция для управляемого создания схемы.
- Gemini `gemini-1.5-flash` для извлечения структурированного события из сырого текста.
- Telegram-бот на aiogram 3.x с командами `/start`, `/search`, `/subscribe`, `/settings`.
- Адаптеры для Telegram/Telethon и HTML-скрейпинга BeautifulSoup.
- Моковые события загружаются автоматически при первом запуске.

## Запуск

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

Для применения миграций в окружении с Alembic используйте `alembic upgrade head`.

Откройте `http://127.0.0.1:8000/docs`. Базовые маршруты: `GET /health`, `GET /events`, `GET /events?city=Алматы&category=startup`, `POST /events`.

Для бота заполните `TELEGRAM_BOT_TOKEN`, затем запустите отдельным процессом:

```bash
python -m app.bot.main
```

Для Gemini заполните `GEMINI_API_KEY`; без ключа extractor работает в локальном fallback-режиме, что позволяет запускать тесты и демо без внешних сервисов.

## Тесты

```bash
pytest -q
```

## Архитектура

`app/main.py` отвечает за HTTP API и жизненный цикл БД. `app/db` содержит модели и seed-данные. `app/ai/extractor.py` изолирует AI-провайдер. `app/scrapers` содержит источники, а `app/bot` отвечает только за Telegram-команды. Для production рекомендуется PostgreSQL, Alembic-миграции, планировщик задач, webhook Telegram и отдельное хранилище секретов.

## Безопасность

Секреты хранятся только в `.env`, который исключён из Git. Токен, опубликованный в переписке, следует немедленно отозвать и перевыпустить через BotFather, после чего сохранить новый токен локально в `.env`.
