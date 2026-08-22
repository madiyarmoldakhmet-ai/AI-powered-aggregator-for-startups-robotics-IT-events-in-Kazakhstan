import asyncio

from app.ai.extractor import EventExtractor
from app.scrapers.telegram import TelegramChannelScraper
from app.scrapers.web import HubWebScraper


def test_telegram_keyword_filter_is_case_insensitive() -> None:
    assert TelegramChannelScraper.matches("Регистрация на WorldSkills Kazakhstan")
    assert TelegramChannelScraper.matches("ХАКАТОН для студентов")
    assert not TelegramChannelScraper.matches("Новости погоды Алматы")


def test_web_parser_returns_matching_items_and_links() -> None:
    html = """
    <main>
      <article><a href="https://example.com/hack">Большой хакатон Astana Hub</a></article>
      <h2>Общая новость без события</h2>
      <article>Startup grant для команд Казахстана</article>
    </main>
    """
    items = HubWebScraper().parse(html, "https://astanahub.com/news")

    assert len(items) == 2
    assert items[0]["link"] == "https://example.com/hack"
    assert all("text" in item for item in items)


def test_extractor_fallback_produces_api_compatible_event() -> None:
    event = asyncio.run(EventExtractor().extract("Almaty Startup Weekend", "https://example.com/event"))

    assert event.title == "Almaty Startup Weekend"
    assert event.link == "https://example.com/event"
    assert event.category == "startup"