import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from core.embedder import get_embedder
from core.models import Topic


class TopicAgent:
    """
    Прикрепляет вопрос к существующей теме или создаёт новую.
    Три зоны: attach / candidate / new.
    """

    def __init__(self, t_high: float = 0.82, t_low: float = 0.68):
        self.t_high = t_high
        self.t_low = t_low

    def _embed(self, text: str) -> np.ndarray:
        return get_embedder().encode([text], normalize_embeddings=True)[0]

    def run(self, question_id: int, question_title: str,
            topics: list[Topic]) -> dict:
        emb = self._embed(question_title)

        if not topics:
            new_id = max((t.id for t in topics), default=0) + 1
            return {
                "action": "new",
                "topic_id": new_id,
                "topic_name": question_title,
                "score": 1.0,
                "reason": "первая тема в системе",
            }

        topic_embs = np.vstack([t.embedding for t in topics])
        sims = cosine_similarity([emb], topic_embs)[0]
        best_idx = int(np.argmax(sims))
        best = topics[best_idx]
        score = float(sims[best_idx])

        if score >= self.t_high:
            return {
                "action": "attach",
                "topic_id": best.id,
                "topic_name": best.name,
                "score": score,
                "reason": f"высокое сходство с темой «{best.name}» ({score:.2f})",
            }

        if score >= self.t_low:
            return {
                "action": "candidate",
                "topic_id": best.id,
                "topic_name": best.name,
                "score": score,
                "reason": f"пограничное сходство с «{best.name}» ({score:.2f}), нужен кандидат",
            }

        new_id = max(t.id for t in topics) + 1
        return {
            "action": "new",
            "topic_id": new_id,
            "topic_name": question_title,
            "score": score,
            "reason": f"ближайшая тема «{best.name}» ниже порога ({score:.2f})",
        }
