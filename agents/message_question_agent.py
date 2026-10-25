import re
from datetime import datetime, timedelta
from typing import Optional

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from core.embedder import get_embedder
from core.models import Message, Question


class QuestionAgent:
    """
    Группирует сообщения вокруг одной задачи.
    Жёсткие связи: reply-цепочки.
    Мягкие связи: эмбеддинг + временной разрыв.
    """

    QUESTION_MARKERS = re.compile(
        r"(\?|кто|когда|где|во сколько|давайте|нужно ли|можно ли)", re.IGNORECASE
    )
    MAX_GAP = timedelta(hours=12)

    def __init__(self, sim_threshold: float = 0.78):
        self.sim_threshold = sim_threshold

    def _is_question_seed(self, m: Message) -> bool:
        return bool(self.QUESTION_MARKERS.search(m.text or ""))

    def _embed(self, texts: list[str]) -> np.ndarray:
        return get_embedder().encode(texts, normalize_embeddings=True)

    def run(self, messages: list[Message]) -> list[Question]:
        messages = sorted(messages, key=lambda m: m.sent_at)
        by_id = {m.id: m for m in messages}

        seeds = [m for m in messages if self._is_question_seed(m)]
        if not seeds:
            return []

        seed_embs = self._embed([s.text for s in seeds])
        clusters: dict[int, list[Message]] = {s.id: [s] for s in seeds}

        for m in messages:
            if m.id in clusters:
                continue

            if m.reply_to and m.reply_to in by_id:
                parent = by_id[m.reply_to]
                for seed_id, members in clusters.items():
                    if parent in members:
                        members.append(m)
                        break
                else:
                    self._attach_by_similarity(m, clusters, seeds, seed_embs)
                continue

            self._attach_by_similarity(m, clusters, seeds, seed_embs)

        return [self._to_question(members) for members in clusters.values()]

    def _attach_by_similarity(self, m, clusters, seeds, seed_embs):
        valid = [
            i for i, s in enumerate(seeds)
            if abs(m.sent_at - s.sent_at) <= self.MAX_GAP
        ]
        if not valid:
            return

        emb = self._embed([m.text])[0]
        sims = cosine_similarity([emb], seed_embs[valid])[0]
        best = int(np.argmax(sims))

        if sims[best] >= self.sim_threshold:
            clusters[seeds[valid[best]].id].append(m)

    def _to_question(self, members: list[Message]) -> Question:
        members = sorted(members, key=lambda x: x.sent_at)
        seed = members[0]

        answer = None
        status = "open"
        for m in members[1:]:
            if not self._is_question_seed(m):
                answer = m.text
                status = "answered"
                break

        conf = sum(self._is_question_seed(m) for m in members) / len(members)

        return Question(
            title=seed.text[:120],
            status=status,
            member_ids=[m.id for m in members],
            answer=answer,
            confidence=round(conf, 2),
        )
