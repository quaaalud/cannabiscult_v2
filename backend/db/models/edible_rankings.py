#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 30 19:48:26 2023

@author: dale
"""

from sqlalchemy import Column, Integer, Float, String, Date, func
from db.base_class import Base


class MysteryEdibleRanking(Base):
    mystery_edible_ranking_id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement="auto",
    )
    cultivator = Column(
        String,
        nullable=False,
        index=True
    )
    strain = Column(
        String,
        nullable=False,
        index=True
    )
    voter_email = Column(
        String,
        nullable=False,
        index=True
    )
    appearance_vote = Column(
        Float,
        nullable=False
    )
    appearance_explanation = Column(
        String,
        nullable=True
    )
    flavor_vote = Column(
        Float,
        nullable=False
    )
    flavor_explanation = Column(
        String,
        nullable=True
    )
    aftertaste_vote = Column(
        Float,
        nullable=False
    )
    aftertaste_explanation = Column(
        String,
        nullable=True
    )
    effects_vote = Column(
        Float,
        nullable=False
    )
    effects_explanation = Column(
        String,
        nullable=True
    )
    date_posted = Column(
        Date,
        default=func.now()
    )
    
    
    
class Vivid_Edible_Ranking(Base):
    vivid_edible_ranking_id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement="auto",
    )
    vivid_edible_id = Column(
        Integer,
        nullable=False,
    )
    strain = Column(
        String,
        nullable=False,
        index=True
    )
    voter_email = Column(
        String,
        nullable=False,
        index=True
    )
    appearance_vote = Column(
        Float,
        nullable=False
    )
    appearance_explanation = Column(
        String,
        nullable=True
    )
    flavor_vote = Column(
        Float,
        nullable=False
    )
    flavor_explanation = Column(
        String,
        nullable=True
    )
    aftertaste_vote = Column(
        Float,
        nullable=False
    )
    aftertaste_explanation = Column(
        String,
        nullable=True
    )
    effects_vote = Column(
        Float,
        nullable=False
    )
    effects_explanation = Column(
        String,
        nullable=True
    )
    date_posted = Column(
        Date,
        default=func.now()
    )
    
    
class Vibe_Edible_Ranking(Base):
    vibe_edible_ranking_id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement="auto",
    )

    vibe_edible_id = Column(
        Integer,
        nullable=False,
    )
    strain = Column(
        String,
        nullable=False,
        index=True
    )
    voter_email = Column(
        String,
        nullable=False,
        index=True
    )
    appearance_vote = Column(
        Float,
        nullable=False
    )
    appearance_explanation = Column(
        String,
        nullable=True
    )
    flavor_vote = Column(
        Float,
        nullable=False
    )
    flavor_explanation = Column(
        String,
        nullable=True
    )
    aftertaste_vote = Column(
        Float,
        nullable=False
    )
    aftertaste_explanation = Column(
        String,
        nullable=True
    )
    effects_vote = Column(
        Float,
        nullable=False
    )
    effects_explanation = Column(
        String,
        nullable=True
    )
    date_posted = Column(
        Date,
        default=func.now()
    )