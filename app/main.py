from contextlib import asynccontextmanager
import asyncio

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from fastapi import Depends, FastAPI, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db.database import Base, engine, get_db, SessionLocal
from app.db.models import Event
from app.db.seed import seed_events
from app.schemas import EventCreate, EventRead
from app.ingest import ingest_sources


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    with next(get_db()) as db:
        if get_settings().seed_mock_events:
            seed_events(db)
    scheduler = AsyncIOScheduler()
    settings = get_settings()

    async def run_ingest() -> None:
        with SessionLocal() as db:
            await ingest_sources(db)

    if settings.scraper_interval_hours > 0:
        scheduler.add_job(run_ingest, "interval", hours=settings.scraper_interval_hours, id="event-ingest", replace_existing=True)
        scheduler.start()
        asyncio.create_task(run_ingest())
    try:
        yield
    finally:
        scheduler.shutdown(wait=False)


app = FastAPI(title=get_settings().app_name, version="1.0.0", lifespan=lifespan)


@app.get("/", tags=["system"])
def root() -> dict[str, str]:
    return {"name": get_settings().app_name, "status": "ok", "docs": "/docs"}


@app.get("/health", tags=["system"])
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/events", response_model=list[EventRead], tags=["events"])
def list_events(city: str | None = None, category: str | None = Query(default=None), db: Session = Depends(get_db)) -> list[Event]:
    query = select(Event).order_by(Event.date)
    if city:
        query = query.where(Event.city == city)
    if category:
        query = query.where(Event.category == category)
    return list(db.scalars(query).all())


@app.get("/events/{event_id}", response_model=EventRead, tags=["events"])
def get_event(event_id: int, db: Session = Depends(get_db)) -> Event:
    event = db.get(Event, event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@app.post("/events", response_model=EventRead, status_code=201, tags=["events"])
def create_event(payload: EventCreate, db: Session = Depends(get_db)) -> Event:
    event = Event(**payload.model_dump())
    db.add(event)
    db.commit()
    db.refresh(event)
    return event
