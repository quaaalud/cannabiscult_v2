#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov  5 17:09:03 2023

@author: dale
"""
from sqlalchemy import (
    Column,
    String,
    BigInteger,
    Date,
    Boolean,
    ForeignKey,
    Text,
    ARRAY,
    CheckConstraint,
    Enum,
    Integer,
    Float,
    func,
)
from db.base_class import Base, StrainCategory


class Flower(Base):
    __table_args__ = {"schema": "public"}
    flower_id = Column(BigInteger, primary_key=True, index=True, autoincrement="auto", nullable=False)
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
        default=True,
    )
    product_type = Column(
        String,
        default="flower",
    )


class Flower_Description(Base):
    __table_args__ = {"schema": "public"}
    description_id = Column(BigInteger, primary_key=True, autoincrement=True)
    flower_id = Column(BigInteger, ForeignKey("public.flower.flower_id", onupdate="CASCADE"), nullable=True)
    description = Column(Text, nullable=False, default="Coming Soon", server_default="Coming Soon")
    effects = Column(Text, nullable=False, default="Coming Soon", server_default="Coming Soon")
    lineage = Column(Text, nullable=False, default="Coming Soon", server_default="Coming Soon")
    terpenes_list = Column(ARRAY(Text), nullable=True)
    cultivar_email = Column(Text, ForeignKey("mysteryvoter.email"), nullable=False)
    strain_category = Column(
        Enum(StrainCategory, name="strain_category"),
        nullable=False,
        server_default="cult_pack",
    )

    __table_args__ = (
        CheckConstraint("length(description) < 1500", name="flower_descriptions_description_check"),
        CheckConstraint("length(effects) < 1500", name="flower_descriptions_effects_check"),
        CheckConstraint("length(lineage) < 1500", name="flower_descriptions_lineage_check"),
    )


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
