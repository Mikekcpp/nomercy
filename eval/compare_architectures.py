"""
Сравнение архитектур из слайда 12.
Заглушки: full_text / rag / rag_by_questions / full_system.
"""

ARCHITECTURES = ["full_text", "rag", "rag_by_questions", "full_system"]


def evaluate(architecture: str) -> dict:
    # TODO: реализовать каждый вариант и прогнать по eval/corpus.jsonl
    return {"architecture": architecture, "task_success": 0.0}


def run():
    for arch in ARCHITECTURES:
        print(evaluate(arch))


if __name__ == "__main__":
    run()
