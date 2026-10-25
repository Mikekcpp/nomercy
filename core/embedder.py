"""
Ленивая загрузка моделей: один экземпляр на процесс.
Так SentenceTransformer не грузится 5 раз из разных агентов.
"""
from functools import lru_cache

from sentence_transformers import SentenceTransformer, CrossEncoder


@lru_cache(maxsize=1)
def get_embedder() -> SentenceTransformer:
    return SentenceTransformer("intfloat/multilingual-e5-small")


@lru_cache(maxsize=1)
def get_reranker() -> CrossEncoder:
    return CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
