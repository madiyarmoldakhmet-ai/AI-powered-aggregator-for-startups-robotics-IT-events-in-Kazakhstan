import json
from typing import Any

from app.config import get_settings
from app.schemas import EventBase

EXTRACTION_PROMPT = """Извлеки событие из текста и верни только JSON с полями: title, city, format (online/offline), date, deadline, category (robotics/startup/hackathon/gamedev/cybersecurity), description, link. Если данных нет, используй null. Текст: {text}"""


class EventExtractor:
    async def extract(self, raw_text: str, source_link: str = "") -> EventBase:
        settings = get_settings()
        if not settings.gemini_api_key:
            return self._fallback(raw_text, source_link)
        try:
            import google.generativeai as genai

            genai.configure(api_key=settings.gemini_api_key)
            model = genai.GenerativeModel(settings.gemini_model)
            response = await model.generate_content_async(EXTRACTION_PROMPT.format(text=raw_text))
            text = response.text.strip().removeprefix("```json").removesuffix("```").strip()
            payload: dict[str, Any] = json.loads(text)
            payload["link"] = payload.get("link") or source_link
            return EventBase.model_validate(payload)
        except ImportError:
            return self._fallback(raw_text, source_link)
        except (json.JSONDecodeError, ValueError, RuntimeError) as exc:
            raise RuntimeError("Gemini extraction failed") from exc

    @staticmethod
    def _fallback(raw_text: str, source_link: str) -> EventBase:
        first_line = raw_text.strip().splitlines()[0] if raw_text.strip() else "Новое событие"
        return EventBase(title=first_line[:300], city="Online", format="online", date="Не указана", deadline=None, category="startup", description=raw_text[:2000], link=source_link)
