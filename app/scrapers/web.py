from bs4 import BeautifulSoup


class HubWebScraper:
    """Small HTML adapter; scheduling and persistence stay in the application layer."""

    def parse(self, html: str, source_url: str) -> list[dict[str, str]]:
        soup = BeautifulSoup(html, "html.parser")
        return [{"title": heading.get_text(" ", strip=True), "link": source_url} for heading in soup.select("h1, h2, h3") if heading.get_text(strip=True)]
