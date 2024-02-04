#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 30 21:57:01 2023

@author: dale
"""


from sqlalchemy import Column, String, BigInteger, Boolean
from db.base_class import Base


class Edible(Base):
    __table_args__ = {"schema": "public"}

    edible_id = Column(
        BigInteger, primary_key=True, index=True, autoincrement="auto", nullable=False
    )
    cultivator = Column(String, nullable=False)
    strain = Column(String, nullable=False)
    card_path = Column(String, nullable=True)
    voting_open = Column(
        Boolean,
        default=True,
        nullable=False,
    )
    is_mystery = Column(
        Boolean,
        default=False,
    )


class MysteryEdible(Base):
    __table_args__ = {"schema": "public"}

    mystery_edible_id = Column(
        BigInteger, primary_key=True, index=True, autoincrement="auto", nullable=False
    )
    cultivator = Column(String, nullable=False)
    strain = Column(String, nullable=False)
    card_path = Column(String, nullable=True)


class VividEdible(Base):
    __table_args__ = {"schema": "public"}

    vivid_edible_id = Column(
        BigInteger, primary_key=True, index=True, autoincrement="auto", nullable=False
    )
    strain = Column(String, nullable=False)
    card_path = Column(String, nullable=True)


class VibeEdible(Base):
    __table_args__ = {"schema": "public"}

    vibe_edible_id = Column(
        BigInteger, primary_key=True, index=True, autoincrement="auto", nullable=False
    )
    strain = Column(String, nullable=False)
    card_path = Column(String, nullable=True)
    cultivator = Column(String, server_default="Vibe", nullable=True)
