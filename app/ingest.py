from collections.abc import Iterable

from aiogram import Bot
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ai.extractor import EventExtractor
from app.config import get_settings
from app.db.models import Event, Subscriber
from app.scrapers.telegram import TelegramChannelScraper
from app.scrapers.web import HubWebScraper


async def ingest_sources(db: Session, telegram: TelegramChannelScraper | None = None, web: HubWebScraper | None = None) -> int:
    settings = get_settings()
    telegram = telegram or TelegramChannelScraper()
    web = web or HubWebScraper()
    raw_items: list[dict[str, str]] = []
    if settings.telegram_api_id and settings.telegram_api_hash:
        raw_items.extend(await telegram.collect_all())
    raw_items.extend(await web.collect())
    added: list[Event] = []
    for item in raw_items:
        try:
            event_data = await EventExtractor().extract(item["text"], item["link"])
        except RuntimeError:
            continue
        if db.scalar(select(Event.id).where(Event.link == event_data.link)) is not None:
            continue
        event = Event(**event_data.model_dump(), source=item.get("source", "scraper"))
        db.add(event)
        added.append(event)
    if added:
        db.commit()
        await notify_subscribers(db, added)
    return len(added)


async def notify_subscribers(db: Session, events: Iterable[Event]) -> None:
    token = get_settings().telegram_bot_token
    if not token:
        return
    bot = Bot(token=token)
    try:
        subscribers = db.scalars(select(Subscriber)).all()
        message = "\n\n".join(f"{event.title}\n{event.date}, {event.city}\n{event.link}" for event in events)
        for subscriber in subscribers:
            try:
                await bot.send_message(subscriber.chat_id, message)
            except Exception:
                continue
    finally:
        await bot.session.close()