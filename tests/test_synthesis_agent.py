from agents.synthesis_agent import SynthesisAgent


def test_claim_without_source_is_unsupported():
    agent = SynthesisAgent(llm_call=lambda p: "Факт без источника.")
    answer = agent.run("вопрос", context=[{"id": 1, "text": "факт"}])
    assert answer.grounded is False
    assert answer.uncertainties
