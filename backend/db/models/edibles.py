#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 30 21:57:01 2023

@author: dale
"""


from sqlalchemy import (
    Column,
    String,
    BigInteger,
    Boolean,
    Text,
    ForeignKey,
    ARRAY,
    Enum,
    CheckConstraint,
    Integer,
    Float,
    Date,
    func,
)
from db.base_class import Base, StrainCategory


class Edible(Base):
    __table_args__ = {"schema": "public"}

    edible_id = Column(BigInteger, primary_key=True, index=True, autoincrement="auto", nullable=False)
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
    product_type = Column(Text, default="edible")


class VibeEdible(Base):
    __table_args__ = {"schema": "public"}

    vibe_edible_id = Column(BigInteger, primary_key=True, index=True, autoincrement="auto", nullable=False)
    strain = Column(String, nullable=False)
    card_path = Column(String, nullable=True)
    cultivator = Column(String, server_default="Vibe", nullable=True)
    product_type = Column(Text, default="edible")


class Edible_Description(Base):
    __table_args__ = {"schema": "public"}
    description_id = Column(BigInteger, primary_key=True, autoincrement=True)
    edible_id = Column(
        BigInteger,
        ForeignKey("public.edible.edible_id", onupdate="CASCADE"),
        nullable=True,
    )
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
        CheckConstraint(
            "length(description) < 1500",
            name="edible_descriptions_description_check",
        ),
        CheckConstraint("length(effects) < 1500", name="edible_descriptions_effects_check"),
        CheckConstraint("length(lineage) < 1500", name="edible_descriptions_lineage_check"),
    )


class Edible_Ranking(Base):
    edible_ranking_id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement="auto",
    )
    edible_id = Column(BigInteger, ForeignKey("public.edible.edible_id", onupdate="CASCADE"), nullable=False)
    cultivator = Column(String, nullable=False, index=True)
    strain = Column(String, nullable=False, index=True)
    connoisseur = Column(String, nullable=False, index=True)
    appearance_rating = Column(Float, nullable=False)
    appearance_explanation = Column(String, nullable=True)
    flavor_rating = Column(Float, nullable=False)
    flavor_explanation = Column(String, nullable=True)
    feel_rating = Column(Float, nullable=False)
    feel_explanation = Column(String, nullable=True)
    chew_rating = Column(Float, nullable=False)
    chew_explanation = Column(String, nullable=True)
    aftertaste_rating = Column(Float, nullable=False)
    aftertaste_explanation = Column(String, nullable=True)
    effects_rating = Column(Float, nullable=False)
    effects_explanation = Column(String, nullable=True)
    date_posted = Column(Date, default=func.now())


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
    strain = Column(String, nullable=False, index=True)
    cultivator = Column(
        String,
    )
    flavor = Column(
        String,
        nullable=False,
    )
    connoisseur = Column(String, nullable=False, index=True)
    appearance_rating = Column(Float, nullable=False)
    appearance_explanation = Column(String, nullable=True)
    feel_rating = Column(Float, nullable=False)
    feel_explanation = Column(String, nullable=True)
    flavor_rating = Column(Float, nullable=False)
    flavor_explanation = Column(String, nullable=True)
    chew_rating = Column(Float, nullable=False)
    chew_explanation = Column(String, nullable=True)
    effects_rating = Column(Float, nullable=False)
    effects_explanation = Column(String, nullable=True)
    date_posted = Column(Date, default=func.now())
