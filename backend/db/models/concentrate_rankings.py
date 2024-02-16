#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov  5 17:18:35 2023

@author: dale
"""

from sqlalchemy import Column, Integer, Float, String, Date, func
from db.base_class import Base


class Concentrate_Ranking(Base):
    concentrate_ranking_id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement="auto",
    )
    cultivator = Column(String, index=True)
    strain = Column(String, index=True)
    connoisseur = Column(String, index=True)
    color_rating = Column(Float, nullable=False)
    consistency_rating = Column(Float, nullable=False)
    smell_rating = Column(Float, nullable=False)
    flavor_rating = Column(Float, nullable=False)
    harshness_rating = Column(Float, nullable=False)
    residuals_rating = Column(Float, nullable=False)
    effects_rating = Column(Float, nullable=False)
    color_explanation = Column(String(500), nullable=True)
    consistency_explanation = Column(String(500), nullable=True)
    flavor_explanation = Column(String(500), nullable=True)
    smell_explanation = Column(String(500), nullable=True)
    harshness_explanation = Column(String(500), nullable=True)
    residuals_explanation = Column(String(500), nullable=True)
    effects_explanation = Column(String(500), nullable=True)
    pack_code = Column(String, nullable=True, server_default="Not Provided", default="Not Provided")

    date_posted = Column(
        Date,
        default=func.now(),
        nullable=False,
    )
    concentrate_id = Column(Integer, nullable=False)


class Hidden_Concentrate_Ranking(Base):
    hidden_concentrate_ranking_id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement="auto",
    )
    cultivator = Column(String, index=True)
    strain = Column(String, index=True)
    connoisseur = Column(String, index=True)
    color_rating = Column(Float, nullable=False)
    consistency_rating = Column(Float, nullable=False)
    smell_rating = Column(Float, nullable=False)
    flavor_rating = Column(Float, nullable=False)
    harshness_rating = Column(Float, nullable=False)
    residuals_rating = Column(Float, nullable=False)
    effects_rating = Column(Float, nullable=False)
    color_explanation = Column(String(500))
    consistency_explanation = Column(String(500))
    flavor_explanation = Column(String(500))
    smell_explanation = Column(String(500))
    harshness_explanation = Column(String(500))
    residuals_explanation = Column(String(500))
    effects_explanation = Column(String(500))

    # pack_code = Column(String(500), nullable=True)

    date_posted = Column(
        Date,
        default=func.now(),
        nullable=False,
    )


class Vibe_Concentrate_Ranking(Base):
    vibe_concentrate_ranking_id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement="auto",
    )
    cultivator = Column(String, index=True)
    strain = Column(String, index=True)
    connoisseur = Column(String, index=True)
    color_rating = Column(Float, nullable=False)
    consistency_rating = Column(Float, nullable=False)
    smell_rating = Column(Float, nullable=False)
    flavor_rating = Column(Float, nullable=False)
    harshness_rating = Column(Float, nullable=False)
    residuals_rating = Column(Float, nullable=False)
    effects_rating = Column(Float, nullable=False)
    color_explanation = Column(String(500))
    consistency_explanation = Column(String(500))
    flavor_explanation = Column(String(500))
    smell_explanation = Column(String(500))
    harshness_explanation = Column(String(500))
    residuals_explanation = Column(String(500))
    effects_explanation = Column(String(500))
    concentrate_id = Column(Integer, nullable=False)

    date_posted = Column(
        Date,
        default=func.now(),
        nullable=False,
    )
