from datetime import datetime

from agents.message_question_agent import QuestionAgent
from core.models import Message


def test_does_not_merge_unrelated():
    msgs = [
        Message(1, 1, 1, "Во сколько начинается конференция?", datetime(2024, 10, 1, 10)),
        Message(2, 1, 2, "Купил хлеб", datetime(2024, 10, 1, 11)),
    ]
    qs = QuestionAgent().run(msgs)
    assert len(qs) == 1
    assert qs[0].status == "open"
