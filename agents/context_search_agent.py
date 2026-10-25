import numpy as np

from core.embedder import get_embedder, get_reranker
from core.models import SearchPlan


class ContextSearchAgent:
    """
    Планирует поиск, расширяет запрос, собирает минимальный пакет.
    """

    def __init__(self):
        self.keyword_map = {
            "конференц": "event",
            "митап": "event",
            "во сколько": "event",
            "кто": "question",
            "что известно": "topic",
        }

    def plan(self, query: str) -> SearchPlan:
        q = query.lower()
        indexes = {"messages"}
        for kw, idx in self.keyword_map.items():
            if kw in q:
                indexes.add(idx)

        keywords = [w for w in q.split() if len(w) > 2]
        return SearchPlan(indexes=sorted(indexes), keywords=keywords)

    def expand(self, query: str, plan: SearchPlan) -> list[str]:
        return [query] + plan.keywords

    def retrieve(self, expanded: list[str],
                 store: dict[str, list[dict]],
                 k: int = 20) -> list[dict]:
        candidates = []
        query_embs = get_embedder().encode(expanded, normalize_embeddings=True)

        for idx in store:
            for item in store[idx]:
                if "embedding" not in item:
                    continue
                sim = float(np.dot(query_embs.mean(axis=0), item["embedding"]))
                candidates.append({**item, "index": idx, "score": sim})

        seen, uniq = set(), []
        for c in candidates:
            if c["id"] in seen:
                continue
            seen.add(c["id"])
            uniq.append(c)

        return uniq[:k * 5]

    def rerank(self, query: str, candidates: list[dict],
               k: int = 20) -> list[dict]:
        if not candidates:
            return []
        pairs = [(query, c.get("text", "")) for c in candidates]
        scores = get_reranker().predict(pairs)
        ranked = sorted(
            zip(candidates, scores), key=lambda x: x[1], reverse=True
        )
        return [c for c, _ in ranked[:k]]

    def run(self, query: str, store: dict[str, list[dict]]) -> dict:
        plan = self.plan(query)
        expanded = self.expand(query, plan)
        cands = self.retrieve(expanded, store)
        top = self.rerank(query, cands, k=20)

        return {
            "plan": plan,
            "expanded": expanded,
            "context": top,
            "recall_at_20": len(top) / 20.0 if top else 0.0,
        }
