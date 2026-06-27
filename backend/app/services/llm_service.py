"""
wraps openai calls in one place so the agents don't need to know
whether we're actually calling the API or just mocking it out.

honestly added mock mode mostly so i could demo this without burning
through api credits every time i tested something lol
"""
import base64
import json

from app.config import settings

_client = None
if not settings.MOCK_MODE:
    from openai import OpenAI
    _client = OpenAI(api_key=settings.OPENAI_API_KEY)


def is_mock() -> bool:
    return settings.MOCK_MODE


def encode_image(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def vision_chat(image_path: str, prompt: str) -> dict:
    """sends one image + a prompt to gpt-4o vision, expects a json reply"""
    if settings.MOCK_MODE:
        return None  # caller handles mock fallback

    b64 = encode_image(image_path)
    response = _client.chat.completions.create(
        model=settings.OPENAI_VISION_MODEL,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}},
                ],
            }
        ],
        response_format={"type": "json_object"},
        max_tokens=600,
    )
    raw = response.choices[0].message.content
    return json.loads(raw)


def text_chat(prompt: str, json_mode: bool = False) -> str | dict:
    if settings.MOCK_MODE:
        return None

    kwargs = {}
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}

    response = _client.chat.completions.create(
        model=settings.OPENAI_TEXT_MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500,
        **kwargs,
    )
    content = response.choices[0].message.content
    if json_mode:
        return json.loads(content)
    return content


def embed_text(text: str) -> list[float]:
    if settings.MOCK_MODE:
        return None
    response = _client.embeddings.create(model="text-embedding-3-small", input=text)
    return response.data[0].embedding
