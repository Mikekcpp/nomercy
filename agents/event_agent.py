import re
from datetime import datetime
from typing import Optional

from core.models import EventDelta, EventState

DATE_RE = re.compile(r"\b(\d{1,2})[./](\d{1,2})(?:[./](\d{2,4}))?\b")
TIME_RE = re.compile(r"\b(\d{1,2}):(\d{2})\b")
MOVE_WORDS = re.compile(r"(перенос|перенес|сдвиг|изменени)", re.IGNORECASE)
CANCEL_WORDS = re.compile(r"(отмен|не состоится|не будет)", re.IGNORECASE)


class EventAgent:
    """
    Извлекает событие из сообщений и поддерживает current_state.
    Ключевое: дата сообщения != дата события.
    """

    def extract_delta(self, msg_text: str, msg_date: datetime,
                      msg_id: int) -> Optional[EventDelta]:
        event_time = None
        date_match = DATE_RE.search(msg_text)
        time_match = TIME_RE.search(msg_text)

        if date_match:
            day, month = int(date_match.group(1)), int(date_match.group(2))
            year = int(date_match.group(3)) if date_match.group(3) else msg_date.year
            hour = int(time_match.group(1)) if time_match else 0
            minute = int(time_match.group(2)) if time_match else 0
            try:
                event_time = datetime(year, month, day, hour, minute)
            except ValueError:
                event_time = None

        if CANCEL_WORDS.search(msg_text):
            delta_type = "cancelled"
        elif MOVE_WORDS.search(msg_text):
            delta_type = "moved"
        elif event_time:
            delta_type = "announced"
        else:
            delta_type = "confirmed"

        loc_match = re.search(r"в\s+(корпус\w*|ауд\w*|зал\w*)\s*\d*", msg_text, re.I)
        location = loc_match.group(0) if loc_match else None

        if delta_type == "confirmed" and not event_time and not location:
            return None

        return EventDelta(delta_type, event_time, location, msg_id, msg_date)

    def apply(self, state: EventState, delta: EventDelta) -> EventState:
        if delta.type == "cancelled":
            state.status = "cancelled"
        elif delta.type == "moved":
            if delta.event_time:
                state.event_time = delta.event_time
            state.status = "moved"
        elif delta.type == "announced":
            if delta.event_time:
                state.event_time = delta.event_time
            state.status = "announced"

        if delta.location:
            state.location = delta.location

        state.last_msg_id = delta.msg_id
        return state
