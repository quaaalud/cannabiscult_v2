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

    date_posted = Column(
        Date,
        default=func.now(),
        nullable=False,
    )
    pre_roll_id = Column(Integer, nullable=False)
