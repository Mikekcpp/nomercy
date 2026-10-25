from agents.context_search_agent import ContextSearchAgent
from agents.event_agent import EventAgent
from agents.message_question_agent import QuestionAgent
from agents.synthesis_agent import SynthesisAgent
from agents.topic_agent import TopicAgent

from core.llm import llm_call
from core.models import EventState, Message, Topic


class Pipeline:
    """
    Прогоняет сообщения через всех агентов по порядку.
    """

    def __init__(self):
        self.q_agent = QuestionAgent()
        self.t_agent = TopicAgent()
        self.e_agent = EventAgent()
        self.s_agent = ContextSearchAgent()
        self.synth = SynthesisAgent(llm_call=llm_call)

    def ingest(self, messages: list[Message],
               topics: list[Topic],
               events: dict[int, EventState]) -> dict:
        questions = self.q_agent.run(messages)

        topic_results = []
        for q in questions:
            res = self.t_agent.run(question_id=id(q),
                                   question_title=q.title,
                                   topics=topics)
            topic_results.append(res)

        event_updates = []
        for m in messages:
            delta = self.e_agent.extract_delta(m.text, m.sent_at, m.id)
            if delta:
                event_updates.append(delta)

        return {
            "questions": questions,
            "topics": topic_results,
            "event_deltas": event_updates,
        }
