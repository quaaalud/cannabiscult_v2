# -*- coding: utf-8 -*-

import hashlib
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.sql import func
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional
from uuid import UUID
from db.base import MessagesToUsers
from core.config import settings


def generate_body_hash(message_body: str) -> str:
    """Generates a SHA-256 hash for the given message body."""
    return hashlib.sha256(message_body.encode("utf-8")).hexdigest()


@settings.retry_db
async def upsert_message_record(
    db,
    from_phone: str,
    to_phone: str,
    user_id: UUID,
    message_body: str,
    template_id: Optional[UUID] = None,
    status: str = "new",
    message_id: Optional[str] = None,
):
    """
    Maps the text message to the MessagesToUsers record and performs an upsert.
    The unique constraint on (body_hash, from_, to) ensures conflicts are resolved via an update.
    """
    stmt = insert(MessagesToUsers).values(
        from_=from_phone,
        to=to_phone,
        user_id=user_id,
        template_id=template_id,
        body=message_body,
        body_hash=generate_body_hash(message_body),
        status=status,
        message_id=message_id,
    )
    stmt = stmt.on_conflict_do_update(
        constraint="resident_messages_queue_unique_content_hash",
        set_={
            "status": status,
            "message_id": message_id,
            "updated_at": func.now(),
        },
    )
    try:
        db.execute(stmt)
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        raise e


@settings.retry_db
async def update_message_status(
    db,
    from_phone: str,
    to_phone: str,
    message_body: str,
    new_status: str,
    new_message_id: str,
):
    """
    Updates the message record in MessagesToUsers with the new status and Twilio message ID.
    The record is uniquely identified by the combination of the from, to, and computed body hash.
    """
    body_hash = generate_body_hash(message_body)
    try:
        db.query(MessagesToUsers).filter(
            MessagesToUsers.from_ == from_phone,
            MessagesToUsers.to == to_phone,
            MessagesToUsers.body_hash == body_hash
        ).update(
            {
                "status": new_status,
                "message_id": new_message_id,
                "updated_at": func.now(),
            },
            synchronize_session=False
        )
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        raise e
