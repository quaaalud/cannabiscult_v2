#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 30 19:48:26 2023

@author: dale
"""

from sqlalchemy import Column, Integer, Float, String, Date
from db.base_class import Base


class EdibleRankingBase(Base):
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

class MysteryEdibleRanking(EdibleRankingBase):
    mystery_edible_ranking_id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement="auto",
    )
    
    
    
class Vivid_Edible_Ranking(EdibleRankingBase):
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
    
    
class Vibe_Edible_Ranking(EdibleRankingBase):
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