# EventScout KZ: проектные заметки

## Что сделано

- FastAPI API: health-check, список событий, фильтры по городу и категории, получение события по ID и создание события.
- SQLAlchemy-модель `Event`, SQLite по умолчанию, PostgreSQL через `DATABASE_URL`, Alembic migration.
- Seed-данные для локального первого запуска.
- Gemini extractor в `app/ai/extractor.py`: структурированные поля события и локальный fallback без API-ключа.
- Telegram-бот на aiogram: `/start`, `/search`, `/events`, `/subscribe`, `/settings`.
- Таблица `Subscriber`; `/subscribe` сохраняет chat ID.
- Telethon-скрапер публичных каналов с фильтром: `хакатон`, `робототехника`, `startup`, `grant`, `drone`, `Alem`, `WorldSkills`.
- HTML-скрапер BeautifulSoup для открытых страниц и агрегаторов; относительные ссылки преобразуются в абсолютные.
- Ingest-слой: извлечение события, дедупликация по ссылке, сохранение в БД и рассылка новых событий подписчикам.
- APScheduler: автоматический запуск сбора с интервалом из `SCRAPER_INTERVAL_HOURS`, по умолчанию 3 часа.
- Тесты API, фильтрации Telegram, HTML-парсинга и fallback extractor.

## Проверено

- `pytest -q`: все 6 тестов проходят.
- `python -m compileall -q app tests`: успешно.
- `git diff --check`: успешно.
- Alembic migration на чистой SQLite-БД: успешно.
- API запускается через `uvicorn app.main:app --reload`.
- Бот подключается через `python -m app.bot.main`; конфликт polling означает, что запущено больше одного экземпляра.

## Переменные окружения

Скопировать `.env.example` в `.env`. Реальные значения не коммитить и не помещать в этот файл заметок.

- `DATABASE_URL`: строка подключения к БД.
- `TELEGRAM_BOT_TOKEN`: токен BotFather для aiogram. Использовать только свежий токен, который не публиковался.
- `TELEGRAM_API_ID`, `TELEGRAM_API_HASH`: user API credentials для Telethon.
- `TELEGRAM_CHANNELS`: публичные каналы через запятую без обязательного `@`.
- `SCRAPER_URLS`: открытые HTML-источники через запятую.
- `SCRAPER_INTERVAL_HOURS`: период автоматического сбора.
- `GEMINI_API_KEY`, `GEMINI_MODEL`: Gemini; без ключа используется fallback.
- `ADMIN_API_KEY`: зарезервирован под административные функции.

## Текущий запуск

```bash
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
python -m app.bot.main
pytest -q
```

API: `http://127.0.0.1:8000/docs`.
Бот: `https://t.me/eventscout2010_bot`.

Запускать только один процесс `python -m app.bot.main` для одного токена. API и polling запускаются отдельными процессами.

## Что сделать дальше

1. Немедленно отозвать токен, который появлялся в чате и истории терминала, через `@BotFather` (`/revoke`), получить новый и внести его локально в `.env`.
2. Проверить, что `.env` и базы данных игнорируются Git: перед push выполнить `git status` и поиск секретов.
3. Заполнить `TELEGRAM_API_ID` и `TELEGRAM_API_HASH`, если нужен Telethon; при первом подключении Telethon создаст локальную user-сессию `eventscout`.
4. Указать реальные публичные URL в `SCRAPER_URLS`; Instagram и TikTok подключать только через разрешённые открытые страницы или агрегаторы, не обходя авторизацию и ограничения платформ.
5. Запустить `/start`, `/events` и `/subscribe`, затем проверить появление chat ID и тестовую рассылку нового события.
6. Для production добавить retry/backoff и таймауты по источникам, отдельный worker, мониторинг задач, уникальный индекс на ссылку и полноценные фильтры подписчиков.
7. Не использовать seed-данные как production-контент; перейти на PostgreSQL и применять только `alembic upgrade head`.

## Безопасность

- Секреты не записываются в README, тесты, миграции или этот файл.
- Не вставлять токены в команды, которые попадут в shell history; безопаснее отредактировать локальный `.env` или использовать менеджер секретов.
- Если секрет опубликован, считать его скомпрометированным независимо от того, найден ли он в Git.
- Перед публикацией репозитория проверить историю Git и при необходимости удалить секреты из истории после ротации.

## Известные ограничения

- Telethon требует Telegram user API credentials и интерактивную авторизацию сессии; один bot token для этого не подходит.
- HTML-скрапер не является обходом защиты Instagram/TikTok и зависит от доступной разметки страниц.
- Gemini может вернуть невалидные или неполные данные; сейчас такие ошибки пропускаются ingest-слоем.
- Подписки пока общие: фильтры по городу и категории не сохраняются.
- Scheduler работает внутри процесса FastAPI; при нескольких worker-процессах возможны дублирующие задачи, поэтому для production нужен отдельный scheduler/worker.