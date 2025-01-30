#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov  5 17:09:03 2023

@author: dale
"""
import enum
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
from db.base_class import Base


class StrainCategory(str, enum.Enum):
    indica = "indica"
    indica_dominant_hyrbrid = "indica_dominant_hyrbrid"
    hybrid = "hybrid"
    sativa_dominant_hyrbrid = "sativa_dominant_hyrbrid"
    sativa = "sativa"


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
        server_default="hybrid",
    )

    __table_args__ = (
        CheckConstraint("length(description) < 1500", name="flower_descriptions_description_check"),
        CheckConstraint("length(effects) < 1500", name="flower_descriptions_effects_check"),
        CheckConstraint("length(lineage) < 1500", name="flower_descriptions_lineage_check"),
    )


class MysteryFlowerReview(Base):
    id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement="auto",
    )
    cultivator = Column(String, nullable=False, unique=True, index=True)
    strain = Column(String, nullable=False, unique=True, index=True)
    voter_email = Column(String, nullable=False, unique=True, index=True)
    method_of_consumption = Column(
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


class FlowerVoting(Base):
    __table_args__ = {'schema': 'public'}

    id = Column(
        BigInteger,
        primary_key=True,
        index=True,
        autoincrement="auto",
        nullable=False
    )
    created_at = Column(
        Date,
        nullable=False
    )
    cultivator_selected = Column(
        String,
        nullable=False
    )
    strain_selected = Column(
        String,
        nullable=False
    )
    structure_vote = Column(
        Float,
        nullable=False
    )
    structure_explanation = Column(
        String,
        nullable=True
    )
    nose_vote = Column(
        Float,
        nullable=False
    )
    nose_explanation = Column(
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
    effects_vote = Column(
        Float,
        nullable=False
    )
    effects_explanation = Column(
        String,
        nullable=True
    )
    user_email = Column(
        String,
        nullable=True
    )
    flower_id = Column(
        BigInteger,
        nullable=True,
        default=0,
    )


class FlowerReview(Base):
    __table_args__ = {"schema": "public"}

    id = Column(BigInteger, primary_key=True, index=True, autoincrement="auto", nullable=False)
    cultivator = Column(String, nullable=False)
    strain = Column(String, nullable=False)
    overall = Column(Float, nullable=False)
    structure = Column(ARRAY(Float), nullable=False)
    nose = Column(ARRAY(Float), nullable=False)
    flavor = Column(ARRAY(Float), nullable=False)
    effects = Column(ARRAY(Float), nullable=False)
    vote_count = Column(Integer, nullable=False)
    card_path = Column(String, nullable=True)
    terpene_list = Column(ARRAY(String), nullable=True)
