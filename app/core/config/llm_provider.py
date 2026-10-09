import os
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from app.core.config.settings import DEFAULT_MAIN_MODEL, DEFAULT_FAST_MODEL

load_dotenv()


def _build_llm(model: str, temperature: float = 0) -> ChatOpenAI:
    api_key = os.environ.get("OPENROUTER_API_KEY")
    return ChatOpenAI(
        model=model,
        temperature=temperature,
        api_key=api_key or "your_openrouter_key",
        base_url="https://openrouter.ai/api/v1",
        default_headers={
            "HTTP-Referer": "https://localhost",
            "X-Title": "Trust Cart AI"
        }
    )


def load_llm():
    """Main model — used for generation-heavy steps (questions, recommendations)."""
    model = os.environ.get("OPENROUTER_MODEL", DEFAULT_MAIN_MODEL)
    return _build_llm(model)


def load_fast_llm():
    """Fast/cheap model — used for quick classification steps (routing, intent, validation)."""
    model = os.environ.get("OPENROUTER_FAST_MODEL", DEFAULT_FAST_MODEL)
    return _build_llm(model)