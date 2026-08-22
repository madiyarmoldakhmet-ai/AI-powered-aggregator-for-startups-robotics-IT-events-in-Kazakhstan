from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy import select

from app.config import get_settings
from app.db.database import SessionLocal
from app.db.models import Event, Subscriber

router = Router()


@router.message(Command("start"))
async def start(message: Message) -> None:
    await message.answer("Привет! Я EventScout KZ. Найду хакатоны, стартап-мероприятия и соревнования в Казахстане. Используйте /search или /subscribe.")


@router.message(Command("search"))
async def search(message: Message) -> None:
    await message.answer("Поиск событий доступен через API: GET /events?city=Алматы&category=startup")


@router.message(Command("events"))
async def events(message: Message) -> None:
    with SessionLocal() as db:
        stored_events = db.scalars(select(Event)).all()
    upcoming = sorted(
        (event for event in stored_events if event.date != "Не указана"),
        key=lambda event: event.date,
    )[:10]
    if not upcoming:
        await message.answer("Пока новых событий нет.")
        return
    text = "\n\n".join(f"{event.title}\n{event.date}, {event.city}\n{event.link}" for event in upcoming)
    await message.answer(text)


@router.message(Command("subscribe"))
async def subscribe(message: Message) -> None:
    if message.chat:
        with SessionLocal() as db:
            if db.get(Subscriber, message.chat.id) is None:
                db.add(Subscriber(chat_id=message.chat.id))
                db.commit()
    await message.answer("Вы подписаны на новые события EventScout KZ.")


@router.message(Command("settings"))
async def settings(message: Message) -> None:
    await message.answer("Настройки: города и категории можно выбрать в API-интерфейсе EventScout KZ.")


def build_router() -> Router:
    return router
