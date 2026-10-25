"""
Загрузчик сообщений из Telegram через Telethon.
Требует TELEGRAM_API_ID, TELEGRAM_API_HASH в окружении.
"""
import os
from datetime import datetime

from telethon.sync import TelegramClient

from core.models import Message


async def load_messages(chat: str, limit: int = 1000) -> list[Message]:
    api_id = int(os.environ["TELEGRAM_API_ID"])
    api_hash = os.environ["TELEGRAM_API_HASH"]

    messages: list[Message] = []
    async with TelegramClient("nomercy_session", api_id, api_hash) as client:
        async for m in client.iter_messages(chat, limit=limit):
            if not m.text:
                continue
            messages.append(
                Message(
                    id=m.id,
                    chat_id=m.chat_id,
                    author_id=m.sender_id or 0,
                    text=m.text,
                    sent_at=m.date or datetime.utcnow(),
                    reply_to=m.reply_to_msg_id,
                )
            )
    return messages
