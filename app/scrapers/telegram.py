class TelegramChannelScraper:
    """Telethon integration point. Credentials and channel selection are deployment concerns."""

    async def collect(self, channel: str, limit: int = 20) -> list[str]:
        try:
            from telethon import TelegramClient
        except ImportError as exc:
            raise RuntimeError("Install Telethon to enable Telegram collection") from exc
        del TelegramClient, channel, limit
        raise NotImplementedError("Configure Telethon API credentials before collecting")
