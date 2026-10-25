import numpy as np

from agents.topic_agent import TopicAgent
from core.models import Topic


def test_creates_new_topic_when_no_topics():
    res = TopicAgent().run(question_id=1, question_title="Конференция по ИИ", topics=[])
    assert res["action"] == "new"
