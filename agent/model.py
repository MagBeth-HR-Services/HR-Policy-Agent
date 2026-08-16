import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def create_chat_model() -> ChatOpenAI:
    """Create the OpenRouter chat model used by the agent."""
    load_dotenv(PROJECT_ROOT / ".env")

    api_key = os.getenv("OPENROUTER_API_KEY")
    model_name = os.getenv("OPENROUTER_MODEL")

    if not api_key:
        raise ValueError(
            "OPENROUTER_API_KEY is missing from .env."
        )

    if not model_name:
        raise ValueError(
            "OPENROUTER_MODEL is missing from .env."
        )

    return ChatOpenAI(
        model=model_name,
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1",
        temperature=0,
        timeout=60,
        max_retries=2,
    )