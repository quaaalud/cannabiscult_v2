#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 11 21:48:19 2023

@author: dale
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    Date,
    ForeignKey,
    BigInteger,
    JSON,
    TIMESTAMP,
    Text,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from db.base_class import Base


class MysteryVoter(Base):
    id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement="auto",
    )
    email = Column(String, nullable=False, unique=True, index=True)
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


class Vibe_Edible_Voter(Base):
    id = Column(Integer, primary_key=True, index=True, autoincrement="auto")
    mystery_voter_id = Column(Integer, ForeignKey("mysteryvoter.id"), nullable=False)

    mystery_voter = relationship("MysteryVoter", back_populates="vibe_edible_voters")

MysteryVoter.vibe_edible_voters = relationship(
    "Vibe_Edible_Voter", order_by=Vibe_Edible_Voter.id, back_populates="mystery_voter"
)

class StrainGuess(Base):
    __tablename__ = "strain_guess"

    guess_id = Column(BigInteger, primary_key=True, autoincrement=True)
    strain_guesses = Column(JSON, nullable=False)
    date_posted = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    email = Column(Text, ForeignKey("mysteryvoter.email", onupdate="CASCADE"), nullable=True)

    # Relationship to link back to the MysteryVoter
    mystery_voter = relationship("MysteryVoter", back_populates="strain_guesses")

    def __repr__(self):
        return f"<StrainGuess(guess_id={self.guess_id}, strain_guesses={self.strain_guesses}, date_posted={self.date_posted}, email={self.email})>"


# Add a corresponding relationship in the MysteryVoter model
MysteryVoter.strain_guesses = relationship(
    "StrainGuess", order_by=StrainGuess.guess_id, back_populates="mystery_voter"
)
