# -*- coding: utf-8 -*-
import uuid
from typing import Any
from sqlalchemy import (
    Column,
    String,
    Integer,
    DateTime,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from core.config import settings
from db.base_class import Base


class TwilioTextTemplates(Base):
    __tablename__ = "text_message_templates"
    __table_args__ = {"extend_existing": True}

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    name = Column(String, nullable=True, primary_key=True)
    template_str = Column(String, nullable=False)
    category = Column(String, nullable=False, server_default="contact_attempt")
    created_at: Mapped[Any] = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[Any] = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    sent_messages = relationship("MessagesToUsers", back_populates="template", lazy="noload")


class MessagesToUsers(Base):
    __tablename__ = "messages_to_users"
    __table_args__ = (
        UniqueConstraint("body_hash", "from_", "to", name="resident_messages_queue_unique_content_hash"),
        {"extend_existing": True},
    )

    id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement="auto",
    )
    from_ = Column(String(20), nullable=False, default=settings.twilio_local_phone)
    to = Column(String(20), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.auth_id"), nullable=False, index=True)
    template_id = Column(UUID(as_uuid=True), ForeignKey("text_message_templates.id"), nullable=True)
    body = Column(String, nullable=False)
    body_hash = Column(String, nullable=True)
    status = Column(String, default="new", nullable=False)
    message_id = Column(String(40), nullable=True)
    created_at: Mapped[Any] = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[Any] = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="sent_messages", lazy="noload", uselist=False)
    template = relationship("TwilioTextTemplates", back_populates="sent_messages", lazy="selectin", uselist=False)


class TwilioMessageRecord(Base):
    __tablename__ = "twilio_message_records"
    __table_args__ = (UniqueConstraint("message_id", name="uq_twilio_message_message_id"),)

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )

    message_id = Column(String(40), nullable=False, unique=True)

    version = Column(String, nullable=True, comment="Flattened from _version.")
    body = Column(String, nullable=False, comment="Text message body.")
    num_segments = Column(Integer, nullable=True, comment="Number of message segments.")
    direction = Column(String, nullable=False, comment="Message direction: inbound/outbound.")
    from_ = Column(String, nullable=False, comment="Sender phone number.")
    to = Column(String, nullable=False, comment="Recipient phone number.")
    date_updated = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    error_message = Column(String, nullable=True)
    uri = Column(String, nullable=False)
    account_sid = Column(String, nullable=False)
    num_media = Column(Integer, nullable=True)
    status = Column(String, nullable=False)
    messaging_service_sid = Column(String, nullable=True)
    date_sent = Column(DateTime(timezone=True), nullable=False)
    date_created = Column(DateTime(timezone=True), nullable=False)
    error_code = Column(Integer, nullable=True)
    api_version = Column(String, nullable=False)
    feedback_uri = Column(String, nullable=True, comment="Feedback URI from subresource_uris.")
    media_uri = Column(String, nullable=True, comment="Media URI from subresource_uris.")
    solution_account_sid = Column(String, nullable=True, comment="Solution account_sid from _solution.")
    solution_sid = Column(String, nullable=True, comment="Solution sid from _solution.")
    context = Column(String, nullable=True, comment="Renamed _context field.")
    created_at: Mapped[Any] = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[Any] = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
