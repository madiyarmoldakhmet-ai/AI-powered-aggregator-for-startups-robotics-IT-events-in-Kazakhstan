from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Event

MOCK_EVENTS = [
    {"title": "Astana Robotics Challenge 2026", "city": "Астана", "format": "offline", "date": "2026-10-17", "deadline": "2026-10-01", "category": "robotics", "description": "Открытое соревнование по робототехнике для школьников и студентов.", "link": "https://example.com/robotics", "source": "mock"},
    {"title": "Almaty Startup Weekend", "city": "Алматы", "format": "offline", "date": "2026-09-12", "deadline": "2026-09-05", "category": "startup", "description": "54 часа для проверки идеи, команды и первого прототипа.", "link": "https://example.com/startup", "source": "mock"},
    {"title": "Central Asia Game Jam", "city": "Online", "format": "online", "date": "2026-11-06", "deadline": None, "category": "gamedev", "description": "Международный онлайн-джем для разработчиков игр.", "link": "https://example.com/gamejam", "source": "mock"},
]


def seed_events(db: Session) -> None:
    if db.scalar(select(Event.id).limit(1)) is not None:
        return
    db.add_all(Event(**event) for event in MOCK_EVENTS)
    db.commit()
