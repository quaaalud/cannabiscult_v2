#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov  5 17:09:03 2023

@author: dale
"""

from sqlalchemy import Column, String, BigInteger, Boolean, ForeignKey, Text, ARRAY, CheckConstraint
from db.base_class import Base


class Flower(Base):
    __table_args__ = {"schema": "public"}

    cultivator = Column(String, nullable=False)
    strain = Column(String, nullable=False)
    card_path = Column(String, nullable=True)
    voting_open = Column(
        Boolean,
        default=True,
        nullable=False,
    )
    flower_id = Column(
        BigInteger, primary_key=True, index=True, autoincrement="auto", nullable=False
    )
    is_mystery = Column(
        Boolean,
        default=True,
    )


class Flower_Description(Base):
    __table_args__ = {"schema": "public"}
    description_id = Column(BigInteger, primary_key=True, autoincrement=True)
    flower_id = Column(
        BigInteger, ForeignKey("public.flower.flower_id", onupdate="CASCADE"), nullable=True
    )
    description = Column(Text, nullable=False, default="Coming Soon", server_default="Coming Soon")
    effects = Column(Text, nullable=False, default="Coming Soon", server_default="Coming Soon")
    lineage = Column(Text, nullable=False, default="Coming Soon", server_default="Coming Soon")
    terpenes_list = Column(ARRAY(Text), nullable=True)
    cultivar_email = Column(Text, ForeignKey("mysteryvoter.email"), nullable=False)

    __table_args__ = (
        CheckConstraint("length(description) < 1500", name="flower_descriptions_description_check"),
        CheckConstraint("length(effects) < 1500", name="flower_descriptions_effects_check"),
        CheckConstraint("length(lineage) < 1500", name="flower_descriptions_lineage_check"),
    )
