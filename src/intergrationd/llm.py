from langchain_openai import ChatOpenAI
from src.core.config import LLMSettings, llm_timeout_seconds

def make_chat_model(model: str | None = None) -> ChatOpenAI:
    configured = model or LLMSettings.from_env().model
    timeout = llm_timeout_seconds()
    return ChatOpenAI(
        model=configured,
        timeout=timeout,
        max_retries=0
    )