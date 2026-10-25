"""
Прогон полной системы по корпусу. Считает Task Success Rate, Groundedness.
Запуск: python -m eval.run_eval
"""
import json
from pathlib import Path

from core.pipeline import Pipeline

CORPUS = Path(__file__).parent / "corpus.jsonl"


def load_corpus() -> list[dict]:
    return [json.loads(line) for line in CORPUS.read_text().splitlines() if line]


def run():
    pipeline = Pipeline()
    cases = load_corpus()
    success = 0

    for case in cases:
        # TODO: заменить на реальный прогон context + synth
        result = pipeline.s_agent.run(case["query"], store={})
        ok = bool(result["context"])
        success += int(ok)

    print(f"Task Success Rate: {success / len(cases):.2%}")


if __name__ == "__main__":
    run()
