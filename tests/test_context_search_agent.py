from agents.context_search_agent import ContextSearchAgent


def test_plan_detects_event_index():
    plan = ContextSearchAgent().plan("во сколько конференция?")
    assert "event" in plan.indexes
