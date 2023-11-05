#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 11 21:48:19 2023

@author: dale
"""

from sqlalchemy import Column, Integer, String, Boolean, Date, ForeignKey
from sqlalchemy.orm import relationship

from db.base_class import Base


class MysteryVoter(Base):
    id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement="auto",
    )
    email = Column(
        String,
        nullable=False,
        unique=True,
        index=True
    )
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
    agree_tos = Column(
        Boolean(),
        default=True
    )
    date_posted = Column(
        Date
    )

    
class Vivid_Edible_Voter(Base):
    id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement="auto"
    )
    mystery_voter_id = Column(
        Integer,
        ForeignKey('mysteryvoter.id'),
        nullable=False
    )

    mystery_voter = relationship(
        "MysteryVoter",
        back_populates="vivid_edible_voters"
    )
    
MysteryVoter.vivid_edible_voters = relationship(
    "Vivid_Edible_Voter",
    order_by=Vivid_Edible_Voter.id,
    back_populates="mystery_voter"
)

Vivid_Edible_Voter.mystery_voter = relationship(
    "MysteryVoter",
    back_populates="vivid_edible_voters"
)


class Vibe_Edible_Voter(Base):
    id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement="auto"
    )
    mystery_voter_id = Column(
        Integer,
        ForeignKey('mysteryvoter.id'),
        nullable=False
    )

    mystery_voter = relationship(
        "MysteryVoter",
        back_populates="vivid_edible_voters"
    )
    
MysteryVoter.vibe_edible_voters = relationship(
    "Vibe_Edible_Voter",
    order_by=Vibe_Edible_Voter.id,
    back_populates="mystery_voter"
)

Vibe_Edible_Voter.mystery_voter = relationship(
    "MysteryVoter",
    back_populates="vibe_edible_voters"
)