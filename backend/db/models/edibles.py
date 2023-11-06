#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 30 21:57:01 2023

@author: dale
"""


from sqlalchemy import Column, String, BigInteger
from db.base_class import Base


class _EdibleBase(Base):
    __table_args__ = {'schema': 'public'}
    
    strain = Column(
        String,
        nullable=False
    )
    card_path = Column(
        String,
        nullable=True
    )


class MysteryEdible(_EdibleBase):
    mystery_edible_id = Column(
        BigInteger,
        primary_key=True,
        index=True,
        autoincrement="auto",
        nullable=False
    )
    cultivator = Column(
        String,
        nullable=False
    )


class VividEdible(_EdibleBase):
    vivid_edible_id = Column(
        BigInteger,
        primary_key=True,
        index=True,
        autoincrement="auto",
        nullable=False
    )
    
    
class VibeEdible(_EdibleBase):
    vibe_edible_id = Column(
        BigInteger,
        primary_key=True,
        index=True,
        autoincrement="auto",
        nullable=False
    )