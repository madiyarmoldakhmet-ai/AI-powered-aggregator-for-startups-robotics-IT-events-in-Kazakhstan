from collections.abc import Iterable

from app.config import get_settings


KEYWORDS = ("хакатон", "робототехника", "startup", "grant", "drone", "alem", "worldskills")


class TelegramChannelScraper:
    """Collect matching posts from configured public Telegram channels."""

    def __init__(self, channels: Iterable[str] | None = None) -> None:
        settings = get_settings()
        configured = channels if channels is not None else settings.telegram_channels.split(",")
        self.channels = tuple(channel.strip().lstrip("@") for channel in configured if channel.strip())

    @staticmethod
    def matches(text: str) -> bool:
        return any(keyword in text.casefold() for keyword in KEYWORDS)

    async def collect(self, channel: str | None = None, limit: int = 20) -> list[dict[str, str]]:
        try:
            from telethon import TelegramClient
        except ImportError as exc:
            raise RuntimeError("Install Telethon to enable Telegram collection") from exc
        settings = get_settings()
        if not settings.telegram_api_id or not settings.telegram_api_hash:
            raise RuntimeError("TELEGRAM_API_ID and TELEGRAM_API_HASH are required")
        channels = (channel.lstrip("@"),) if channel else self.channels
        results: list[dict[str, str]] = []
        client = TelegramClient("eventscout", settings.telegram_api_id, settings.telegram_api_hash)
        await client.connect()
        if not await client.is_user_authorized():
            await client.disconnect()
            raise RuntimeError("Telethon session is not authorized; run the setup command interactively once")
        try:
            for channel_name in channels:
                async for message in client.iter_messages(channel_name, limit=limit):
                    text = (message.message or "").strip()
                    if text and self.matches(text):
                        results.append({"text": text, "link": f"https://t.me/{channel_name}/{message.id}", "source": f"telegram:{channel_name}"})
        finally:
            await client.disconnect()
        return results

    async def collect_all(self, limit: int = 20) -> list[dict[str, str]]:
        return await self.collect(limit=limit)
