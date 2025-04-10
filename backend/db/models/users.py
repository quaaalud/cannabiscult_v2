from typing import Any
from sqlalchemy import (
    Column,
    Integer,
    DateTime,
    BigInteger,
    String,
    Boolean,
    Text,
    ForeignKey,
    TIMESTAMP,
    Date,
    UUID,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, Mapped
from db.base_class import Base


class User(Base):
    __table_args__ = {"extend_existing": True}

    username = Column(String, unique=True, nullable=False)
    email = Column(
        String,
        nullable=False,
        unique=True,
        index=True,
        primary_key=True,
    )
    name = Column(
        String,
        nullable=False,
    )
    phone = Column(String, nullable=True)
    zip_code = Column(
        String,
        nullable=False,
    )
    password = Column(String, nullable=False)
    agree_tos = Column(Boolean(), default=True)
    can_vote = Column(Boolean(), default=True)
    is_superuser = Column(Boolean(), default=False)
    auth_id = Column(UUID, nullable=True, unique=True)

    strain_lists = relationship("UserStrainList", back_populates="user")
    sent_messages = relationship(
        "MessagesToUsers", back_populates="user", cascade="all, delete-orphan", passive_deletes=True, lazy="noload"
    )
    settings = relationship(
        "UserSettings",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="noload",
        uselist=False,
    )


class UserStrainList(Base):
    __tablename__ = "user_strain_list"
    __table_args__ = (UniqueConstraint("email", "strain", "cultivator", "product_type", name="uq_user_strain"),)

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    created_at = Column(TIMESTAMP, nullable=False, default=func.now())
    email = Column(
        Text,
        ForeignKey("user.email", onupdate="CASCADE", ondelete="SET NULL"),
        nullable=False,
    )
    strain = Column(Text, nullable=False)
    cultivator = Column(Text, nullable=False)
    to_review = Column(Boolean, nullable=False, default=True)
    product_type = Column(Text, nullable=True)
    strain_notes = Column(Text, nullable=True, default="N/A", server_default="N/A")
    user = relationship("User", back_populates="strain_lists", lazy="noload")


class MysteryVoter(Base):
    __table_args__ = {"extend_existing": True}

    email = Column(String, nullable=False, unique=True, index=True, primary_key=True)
    name = Column(String, nullable=True, unique=False)
    zip_code = Column(String, nullable=True, unique=False)
    phone = Column(String, nullable=True, unique=False)
    industry_employer = Column(String, nullable=True, unique=False)
    industry_job_title = Column(String, nullable=True, unique=False)
    agree_tos = Column(Boolean(), default=True)
    date_posted = Column(Date)

    vibe_edible_voters = relationship("Vibe_Edible_Voter", back_populates="mystery_voter")


class Vibe_Edible_Voter(Base):
    id = Column(Integer, primary_key=True, index=True, autoincrement="auto")
    mystery_voter_email = Column(String, ForeignKey("mysteryvoter.email"), nullable=False)
    mystery_voter = relationship("MysteryVoter", back_populates="vibe_edible_voters")


class MoluvHeadstashBowl(Base):
    __tablename__ = "moluv_headstash_bowl"
    id = Column(Integer, primary_key=True, index=True, autoincrement="auto")
    product_id = Column(Integer, nullable=False)
    product_type = Column(String(20), nullable=False)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    date_posted = Column(Date, server_default=func.now(), nullable=False)
    updated_at = Column(Date, server_default=func.now(), nullable=False)
    __table_args__ = (UniqueConstraint("user_id", "product_type", name="uq_user_product"),)


class UserSettings(Base):
    __tablename__ = "user_settings"
    __table_args__ = {"extend_existing": True}

    user_id = Column(UUID(as_uuid=True), ForeignKey("user.auth_id"), unique=True, index=True, primary_key=True)
    text_settings = Column(JSONB, nullable=True, server_default="{}")
    email_settings = Column(JSONB, nullable=True, server_default="{}")
    site_settings = Column(JSONB, nullable=True, server_default="{}")
    created_at: Mapped[Any] = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[Any] = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="settings", lazy="noload", uselist=False)
