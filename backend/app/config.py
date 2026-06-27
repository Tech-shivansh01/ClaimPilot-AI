import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
    OPENAI_VISION_MODEL = os.getenv("OPENAI_VISION_MODEL", "gpt-4o")
    OPENAI_TEXT_MODEL = os.getenv("OPENAI_TEXT_MODEL", "gpt-4o-mini")

    WEAVIATE_URL = os.getenv("WEAVIATE_URL", "").strip()

    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./claimpilot.db")
    UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploads")

    FRAUD_REVIEW_THRESHOLD = int(os.getenv("FRAUD_REVIEW_THRESHOLD", "70"))

    # comma-separated list, e.g. "http://localhost:3000,https://claimpilot-ai.vercel.app"
    # lets the same backend work for local dev AND a deployed frontend without code edits
    ALLOWED_ORIGINS = [o.strip() for o in os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",") if o.strip()]

    # if there's no API key we fall back to mock responses everywhere
    # so the app still works for a demo without anyone paying for API calls
    MOCK_MODE = OPENAI_API_KEY == ""


settings = Settings()

os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
