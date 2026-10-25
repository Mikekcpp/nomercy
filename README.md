# NoMercy V2

Контекстный слой над Telegram: сообщения → вопросы → темы → события → ответ с источниками.

## Структура

- `agents/` — пять агентов, по одному на файл
- `core/` — общие модели, эмбеддер, LLM-обёртка, оркестратор
- `ingest/` — загрузчик из Telegram
- `tests/` — unit-тесты агентов
- `eval/` — корпус и прогон метрик

## Запуск

```bash
pip install -r requirements.txt
pytest
python -m eval.run_eval
