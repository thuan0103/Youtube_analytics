from dataclasses import dataclass
from dotenv import load_dotenv
import os

load_dotenv()

def llm_timeout_seconds() -> int:
    raw = os.getenv("AI_LLM_TIMEOUT_SECONDS")
    try:
        return max(int(raw), 1)
    except ValueError:
        return 1


@dataclass
class LLMSettings:
    model: str

    @classmethod
    def from_env(cls) -> "LLMSettings":
        model = os.getenv("AI_LLM_MODEL")
        if not model:
            raise RuntimeError("AI_LLM_MODEL is not config")
        if not os.getenv("OPENAI_API_KEY"):
            raise RuntimeError("OPEN_AI_KEY is not config")
        return cls(model=model)

@dataclass(frozen=True)
class LangfuseSettings:
    public_key: str
    secret_key: str
    host: str

    @classmethod
    def is_configured(cls) -> bool:
        return bool(
            os.getenv("LANGFUSE_PUBLIC_KEY")
            and os.getenv("LANGFUSE_SECRET_KEY")
            and os.getenv("LANGFUSE_HOST")
        )

    @classmethod
    def from_env(cls) -> "LangfuseSettings":
        if not cls.is_configured():
            raise RuntimeError(
                "LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY, LANGFUSE_HOST chưa được cấu hình"
            )
        return cls(
            public_key=os.environ["LANGFUSE_PUBLIC_KEY"],
            secret_key=os.environ["LANGFUSE_SECRET_KEY"],
            host=os.environ["LANGFUSE_HOST"],
        )
