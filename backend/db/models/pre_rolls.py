#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov  5 17:09:03 2023

@author: dale
"""

from sqlalchemy import (
    Column,
    BigInteger,
    Text,
    Boolean,
    ForeignKey,
    CheckConstraint,
    Integer,
    Float,
    String,
    Date,
    event,
    func,
)
from sqlalchemy.dialects.postgresql import ARRAY
from db.base_class import Base


class Pre_Roll(Base):
    __table_args__ = {"schema": "public"}

    cultivator = Column(Text, nullable=False)
    strain = Column(Text, nullable=False)
    card_path = Column(Text, nullable=True)
    voting_open = Column(
        Boolean,
        default=True,
        nullable=False,
    )
    pre_roll_id = Column(
        BigInteger, primary_key=True, index=True, autoincrement="auto", nullable=False
    )
    is_mystery = Column(
        Boolean,
        default=True,
    )


class Pre_Roll_Description(Base):
    __table_args__ = {"schema": "public"}
    description_id = Column(BigInteger, primary_key=True, autoincrement=True)
    pre_roll_id = Column(
        BigInteger,
        ForeignKey("public.pre_roll.pre_roll_id", onupdate="CASCADE"),
        nullable=True,
    )
    description = Column(Text, nullable=False, default="Coming Soon", server_default="Coming Soon")
    effects = Column(Text, nullable=False, default="Coming Soon", server_default="Coming Soon")
    lineage = Column(Text, nullable=False, default="Coming Soon", server_default="Coming Soon")
    terpenes_list = Column(ARRAY(Text), nullable=True)
    cultivar_email = Column(
        Text,
        ForeignKey("mysteryvoter.email"),
        nullable=False,
        default="aaron.childs@thesocialoutfitus.com",
    )
    unused1 = Column(Text, nullable=False, default="Coming Soon", server_default="Coming Soon")
    unused2 = Column(Text, nullable=False, default="Coming Soon", server_default="Coming Soon")

    __table_args__ = (
        CheckConstraint(
            "length(description) < 1500", name="pre_roll_descriptions_description_check"
        ),
        CheckConstraint("length(effects) < 1500", name="pre_roll_descriptions_effects_check"),
        CheckConstraint("length(lineage) < 1500", name="pre_roll_descriptions_lineage_check"),
    )


class Pre_Roll_Ranking(Base):
    pre_roll_ranking_id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement="auto",
    )
    cultivator = Column(String, index=True)
    strain = Column(String, index=True)
    connoisseur = Column(String, index=True)
    roll_rating = Column(Float, nullable=True)
    airflow_rating = Column(Float, nullable=True)
    ease_to_light_rating = Column(Float, nullable=True)
    flavor_rating = Column(Float, nullable=True)
    tightness_rating = Column(Float, nullable=True)
    burn_rating = Column(Float, nullable=True)
    effects_rating = Column(Float, nullable=True)
    overall_score = Column(Float, nullable=True, default=0.0)
    roll_explanation = Column(String(500), nullable=True)
    ease_to_light_explanation = Column(String(500), nullable=True)
    flavor_explanation = Column(String(500), nullable=True)
    airflow_explanation = Column(String(500), nullable=True)
    tightness_explanation = Column(String(500), nullable=True)
    burn_explanation = Column(String(500), nullable=True)
    effects_explanation = Column(String(500), nullable=True)
    purchase_bool = Column(Boolean, nullable=True)
    pack_code = Column(String, nullable=True, server_default="Not Provided", default="Not Provided")
    pre_roll_id = Column(Integer, nullable=False)


def calculate_overall_score(mapper, connection, target):
    # List of all rating columns
    rating_columns = [
        "roll_rating",
        "airflow_rating",
        "ease_to_light_rating",
        "flavor_rating",
        "tightness_rating",
        "burn_rating",
        "effects_rating",
    ]
    # Calculate average rating
    ratings = [getattr(target, col) for col in rating_columns if getattr(target, col) is not None]
    if ratings:
        target.overall_score = sum(ratings) / len(ratings)
    else:
        target.overall_score = None  # or a default value


# Event listeners for before insert and update
event.listen(Pre_Roll_Ranking, "before_insert", calculate_overall_score)
event.listen(Pre_Roll_Ranking, "before_update", calculate_overall_score)
