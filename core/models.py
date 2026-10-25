from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

import numpy as np


@dataclass
class Message:
    id: int
    chat_id: int
    author_id: int
    text: str
    sent_at: datetime
    reply_to: Optional[int] = None


@dataclass
class Question:
    title: str
    status: str                       # open / answered / stale
    member_ids: list[int] = field(default_factory=list)
    answer: Optional[str] = None
    confidence: float = 0.0


@dataclass
class Topic:
    id: int
    name: str
    embedding: np.ndarray
    question_ids: list[int] = field(default_factory=list)


@dataclass
class EventDelta:
    type: str                         # announced / moved / cancelled / confirmed
    event_time: Optional[datetime]
    location: Optional[str]
    msg_id: int
    msg_date: datetime


@dataclass
class EventState:
    event_id: int
    title: str
    event_time: Optional[datetime] = None
    location: Optional[str] = None
    status: str = "announced"
    last_msg_id: Optional[int] = None


@dataclass
class Claim:
    text: str
    source_id: Optional[int]
    supported: bool = False


@dataclass
class FinalAnswer:
    summary: str
    claims: list[Claim]
    contradictions: list[str]
    uncertainties: list[str]
    grounded: bool


@dataclass
class SearchPlan:
    indexes: list[str]
    keywords: list[str]
