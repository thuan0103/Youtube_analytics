from __future__ import annotations

import os
from typing import Any

from langfuse import Langfuse, get_client, propagate_attributes

from src.core.config import LangfuseSettings

_initialized = False


def _ensure_client():
    global _initialized
    if not _initialized:
        if LangfuseSettings.is_configured():
            Langfuse(
                public_key=os.environ["LANGFUSE_PUBLIC_KEY"],
                secret_key=os.environ["LANGFUSE_SECRET_KEY"],
                host=os.environ["LANGFUSE_HOST"],
                tracing_enabled=os.environ.get("LANGFUSE_TRACING_ENABLED", "true").lower()
                != "false",
            )
        _initialized = True
    return get_client()


def observation(as_type: str, name: str, **kwargs: Any):
    return _ensure_client().start_as_current_observation(as_type=as_type, name=name, **kwargs)


def request_attributes(*, user_id: str | None = None):
    return propagate_attributes(
        user_id=user_id,
        trace_name="user-request",
    )


def dump_for_trace(value: Any) -> Any:
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json")
    if isinstance(value, dict):
        return {key: dump_for_trace(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [dump_for_trace(item) for item in value]
    return value


def summarize_messages(messages: list) -> list[dict[str, Any]]:
    from langchain_core.messages import AIMessage, BaseMessage

    summary: list[dict[str, Any]] = []
    for message in messages[-12:]:
        if not isinstance(message, BaseMessage):
            continue
        content = message.content
        text = str(content)[:2000] if not isinstance(content, list) else str(content)[:2000]
        entry: dict[str, Any] = {
            "type": message.type,
            "name": getattr(message, "name", None),
            "content_preview": text,
        }
        if isinstance(message, AIMessage) and message.tool_calls:
            entry["tool_calls"] = message.tool_calls
        summary.append(entry)
    return summary


def langchain_callback():
    from langfuse.langchain import CallbackHandler

    _ensure_client()
    return CallbackHandler()


def flush() -> None:
    _ensure_client().flush()
