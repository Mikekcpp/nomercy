from datetime import datetime

from agents.event_agent import EventAgent
from core.models import EventState


def test_event_agent_move_overrides_time():
    agent = EventAgent()
    state = EventState(event_id=1, title="Конференция")

    d1 = agent.extract_delta("Конференция 20 октября в 10:00",
                             datetime(2024, 10, 10), 1)
    agent.apply(state, d1)

    d2 = agent.extract_delta("Переносим на 11:00",
                             datetime(2024, 10, 18), 2)
    agent.apply(state, d2)

    assert state.event_time.hour == 11
    assert state.status == "moved"
