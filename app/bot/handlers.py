from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.config import get_settings

router = Router()


@router.message(Command("start"))
async def start(message: Message) -> None:
    await message.answer("Привет! Я EventScout KZ. Найду хакатоны, стартап-мероприятия и соревнования в Казахстане. Используйте /search или /subscribe.")


@router.message(Command("search"))
async def search(message: Message) -> None:
    await message.answer("Поиск событий доступен через API: GET /events?city=Алматы&category=startup")


@router.message(Command("subscribe"))
async def subscribe(message: Message) -> None:
    await message.answer("Подписка подготовлена. Персональные фильтры будут сохранены в следующей версии.")


@router.message(Command("settings"))
async def settings(message: Message) -> None:
    await message.answer("Настройки: города и категории можно выбрать в API-интерфейсе EventScout KZ.")


def build_router() -> Router:
    return router
