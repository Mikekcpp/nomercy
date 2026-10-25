"""
Обёртка над LLM.
Приватность (слайд 3): по умолчанию внешний LLM запрещён.
Включается только явным вызовом set_privacy_mode(allow_external=True).
"""

_ALLOW_EXTERNAL = False


def set_privacy_mode(allow_external: bool) -> None:
    global _ALLOW_EXTERNAL
    _ALLOW_EXTERNAL = allow_external


def llm_call(prompt: str) -> str:
    if not _ALLOW_EXTERNAL:
        # Локальная модель (Ollama / llama.cpp / vLLM) — заглушка
        return _local_llm(prompt)
    return _external_llm(prompt)


def _local_llm(prompt: str) -> str:
    # TODO: подключить локальную модель, например через ollama
    return ""


def _external_llm(prompt: str) -> str:
    # TODO: подключить внешний API после явного подтверждения пользователя
    return ""
