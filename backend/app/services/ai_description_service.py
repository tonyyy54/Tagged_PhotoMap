import base64
import logging

import httpx

from app.core.config import settings


logger = logging.getLogger(__name__)
RESPONSES_URL = "https://api.openai.com/v1/responses"
DESCRIPTION_PROMPT = (
    "Describe this photo in one concise, factual sentence for a map photo popup. "
    "Mention the visible setting and main subject. Do not guess the exact location, "
    "people's identities, or facts that cannot be confirmed from the image."
)
INSUFFICIENT_QUOTA_DESCRIPTION = "OpenAI API quota is insufficient."


def _extract_output_text(payload: dict) -> str | None:
    for item in payload.get("output", []):
        for content in item.get("content", []):
            if content.get("type") == "output_text":
                text = content.get("text", "").strip()
                if text:
                    return text
    return None


def _extract_error_description(response: httpx.Response) -> str | None:
    if response.status_code != 429:
        return None

    try:
        error_code = response.json().get("error", {}).get("code")
    except ValueError:
        return None
    if error_code == "insufficient_quota":
        return INSUFFICIENT_QUOTA_DESCRIPTION
    return None


async def generate_ai_description(content: bytes, content_type: str) -> str | None:
    if not settings.OPENAI_API_KEY:
        return None

    image_data = base64.b64encode(content).decode("ascii")
    payload = {
        "model": settings.OPENAI_MODEL,
        "input": [
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": DESCRIPTION_PROMPT},
                    {
                        "type": "input_image",
                        "image_url": f"data:{content_type};base64,{image_data}",
                    },
                ],
            }
        ],
    }
    headers = {
        "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=settings.OPENAI_TIMEOUT_SECONDS) as client:
            response = await client.post(RESPONSES_URL, headers=headers, json=payload)
            error_description = _extract_error_description(response)
            if error_description:
                return error_description
            response.raise_for_status()
    except httpx.HTTPError:
        logger.exception("OpenAI image description request failed")
        return None

    try:
        return _extract_output_text(response.json())
    except ValueError:
        logger.exception("OpenAI image description response was not valid JSON")
        return None
