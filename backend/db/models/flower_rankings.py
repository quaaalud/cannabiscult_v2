#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov  5 17:18:35 2023

@author: dale
"""

from sqlalchemy import Column, Integer, Float, String, Date, func
from db.base_class import Base


class Flower_Ranking(Base):
    flower_ranking_id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement="auto",
    )
    cultivator = Column(String, index=True)
    strain = Column(String, index=True)
    connoisseur = Column(String, index=True)
    method_of_consumption = Column(
        String,
        nullable=True,
        unique=False,
    )
    appearance_rating = Column(Float, nullable=False)
    smell_rating = Column(Float, nullable=False)
    freshness_rating = Column(Float, nullable=False)
    flavor_rating = Column(Float, nullable=False)
    harshness_rating = Column(Float, nullable=False)
    effects_rating = Column(Float, nullable=False)
    appearance_explanation = Column(String(500))
    smell_explanation = Column(String(500))
    freshness_explanation = Column(String(500))
    flavor_explanation = Column(String(500))
    harshness_explanation = Column(String(500))
    effects_explanation = Column(String(500))
    pack_code = Column(String(99), nullable=True)

    date_posted = Column(
        Date,
        default=func.now(),
        nullable=False,
    )
    flower_id = Column(Integer, nullable=False)


class Hidden_Flower_Ranking(Base):
    hidden_flower_ranking_id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement="auto",
    )
    strain = Column(String, index=True)
    method_of_consumption = Column(
        String,
        nullable=True,
        unique=False,
    )
    connoisseur = Column(String, index=True)
    appearance_rating = Column(Float, nullable=False)
    smell_rating = Column(Float, nullable=False)
    freshness_rating = Column(Float, nullable=False)
    flavor_rating = Column(Float, nullable=False)
    harshness_rating = Column(Float, nullable=False)
    effects_rating = Column(Float, nullable=False)
    appearance_explanation = Column(String(500))
    smell_explanation = Column(String(500))
    freshness_explanation = Column(String(500))
    flavor_explanation = Column(String(500))
    harshness_explanation = Column(String(500))
    effects_explanation = Column(String(500))
    pack_code = Column(String(99), nullable=True)

    date_posted = Column(
        Date,
        default=func.now(),
        nullable=False,
    )
    flower_id = Column(Integer, nullable=False)
