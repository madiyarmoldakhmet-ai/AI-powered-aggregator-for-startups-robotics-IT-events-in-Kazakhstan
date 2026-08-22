from bs4 import BeautifulSoup
import httpx

from app.config import get_settings
from app.ai.extractor import EventExtractor


KEYWORDS = ("хакатон", "робототехника", "startup", "grant", "drone", "alem", "worldskills")


class HubWebScraper:
    """Small HTML adapter; scheduling and persistence stay in the application layer."""

    def parse(self, html: str, source_url: str) -> list[dict[str, str]]:
        soup = BeautifulSoup(html, "html.parser")
        results = []
        for item in soup.select("article, li, h1, h2, h3"):
            text = item.get_text(" ", strip=True)
            if not text or not any(keyword in text.casefold() for keyword in KEYWORDS):
                continue
            anchor = item.select_one("a[href]") or item.find_parent("a", href=True)
            link = anchor.get("href", source_url) if anchor else source_url
            results.append({"text": text, "link": link if link.startswith("http") else source_url, "source": source_url})
        return results

    async def collect(self, urls: list[str] | None = None, limit: int = 20) -> list[dict[str, str]]:
        configured = urls or [url.strip() for url in get_settings().scraper_urls.split(",") if url.strip()]
        results: list[dict[str, str]] = []
        async with httpx.AsyncClient(timeout=20, follow_redirects=True, headers={"User-Agent": "EventScout-KZ/1.0"}) as client:
            for url in configured:
                response = await client.get(url)
                response.raise_for_status()
                results.extend(self.parse(response.text, str(response.url))[:limit])
        return results[:limit]

    async def collect_events(self, extractor: EventExtractor | None = None, urls: list[str] | None = None, limit: int = 20):
        extractor = extractor or EventExtractor()
        return [await extractor.extract(item["text"], item["link"]) for item in await self.collect(urls, limit)]
