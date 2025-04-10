# -*- coding: utf-8 -*-

import hashlib
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.sql import func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional, Dict, List
from uuid import UUID
from db.base import MessagesToUsers, TwilioMessageRecord
from backend.twilio.twilio_base import twilio_client
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


@settings.retry_db
async def get_latest_twilio_message_created_at(db: Session) -> datetime:
    """
    Returns the newest created_at datetime from the TwilioMessageRecord table.
    If no records exist, returns a sensible default (e.g., datetime(2025, 1, 1)).
    """
    try:
        latest_created_at = db.query(func.max(TwilioMessageRecord.created_at)).scalar()
        if not latest_created_at:
            latest_created_at = datetime(2025, 1, 1)
        return latest_created_at
    except Exception as e:
        db.rollback()
        raise e


async def get_new_twilio_messages(db: Session) -> Dict | None:
    newest_message_date = await get_latest_twilio_message_created_at(db)
    new_messages = await twilio_client._get_new_messages(newest_message_date=newest_message_date)
    return new_messages


async def upsert_twilio_message(db, message_data: dict):
    stmt = insert(TwilioMessageRecord).values(**message_data)
    stmt = stmt.on_conflict_do_update(
        constraint="uq_twilio_message_message_id",
        set_={
            "body": message_data.get("body"),
            "status": message_data.get("status"),
            "date_updated": func.now(),
        }
    )
    db.execute(stmt)
    db.commit()


async def bulk_upsert_twilio_messages(db: Session, validated_messages: List) -> None:
    if not validated_messages:
        return
    messages = [msg.model_dump() for msg in validated_messages]
    stmt = insert(TwilioMessageRecord).values(messages)
    stmt = stmt.on_conflict_do_update(
        constraint="uq_twilio_message_message_id",
        set_={
            "body": stmt.excluded.body,
            "status": stmt.excluded.status,
            "date_updated": func.now(),
        }
    )
    db.execute(stmt)
    db.commit()
