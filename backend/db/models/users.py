from sqlalchemy import (
    Column,
    Integer,
    BigInteger,
    String,
    Boolean,
    Text,
    ForeignKey,
    TIMESTAMP,
    Date,
    UUID,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from db.base_class import Base


class User(Base):
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
    auth_id = Column(UUID, nullable=True)
    strain_lists = relationship("UserStrainList", back_populates="user")


class UserStrainList(Base):
    __tablename__ = "user_strain_list"

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
    user = relationship("User", back_populates="strain_lists")


class MysteryVoter(Base):
    __table_args__ = {'extend_existing': True}

    email = Column(String, nullable=False, unique=True, index=True, primary_key=True)
    name = Column(
        String,
        nullable=True,
        unique=False,
    )
    zip_code = Column(
        String,
        nullable=True,
        unique=False,
    )
    phone = Column(
        String,
        nullable=True,
        unique=False,
    )
    industry_employer = Column(
        String,
        nullable=True,
        unique=False,
    )
    industry_job_title = Column(
        String,
        nullable=True,
        unique=False,
    )
    agree_tos = Column(Boolean(), default=True)
    date_posted = Column(Date)

    vibe_edible_voters = relationship("Vibe_Edible_Voter", back_populates="mystery_voter")


class Vibe_Edible_Voter(Base):
    id = Column(Integer, primary_key=True, index=True, autoincrement="auto")
    mystery_voter_email = Column(String, ForeignKey("mysteryvoter.email"), nullable=False)
    mystery_voter = relationship("MysteryVoter", back_populates="vibe_edible_voters")
