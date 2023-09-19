#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 13 19:34:01 2023

@author: dale
"""

from sqlalchemy import Column, Integer, Float, String
from db.base_class import Base

class MysteryFlowerReview(Base):
    id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement="auto",
    )
    cultivator = Column(
        String,
        nullable=False,
        unique=True,
        index=True
    )
    strain = Column(
        String,
        nullable=False,
        unique=True,
        index=True
    )
    voter_email = Column(
        String,
        nullable=False,
        unique=True,
        index=True
    )
    method_of_consumption = Column(
        String,
        nullable=True,
        unique=False,
    )
    mystery_sight_vote = Column(
        Float,
        nullable=True,
        unique=False,
    )
    mystery_sight_explanation = Column(
        String,
        nullable=True,
        unique=False,
    )
    mystery_size_vote = Column(
        Float,
        nullable=True,
        unique=False,
    )
    mystery_size_explanation = Column(
        String,
        nullable=True,
        unique=False,
    )
    mystery_structure_vote = Column(
        Float,
        nullable=True,
        unique=False,
    )
    mystery_structure_explanation = Column(
        String,
        nullable=True,
        unique=False,
    )
    mystery_smell_vote = Column(
        Float,
        nullable=True,
        unique=False,
    )
    mystery_smell_explanation = Column(
        String,
        nullable=True,
        unique=False,
    )
    mystery_freshness_vote = Column(
        Float,
        nullable=True,
        unique=False,
    )
    mystery_freshness_explanation = Column(
        String,
        nullable=True,
        unique=False,
    )
    mystery_flavor_vote = Column(
        Float,
        nullable=True,
        unique=False,
    )
    mystery_flavor_explanation = Column(
        String,
        nullable=True,
        unique=False,
    )
    mystery_effects_vote = Column(
        Float,
        nullable=True,
        unique=False,
    )
    mystery_effects_explanation = Column(
        String,
        nullable=True,
        unique=False,
    )
    mystery_smoothness_vote = Column(
        Float,
        nullable=True,
        unique=False,
    )
    mystery_smoothness_explanation = Column(
        String,
        nullable=True,
        unique=False,
    )