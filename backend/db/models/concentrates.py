#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov  5 17:09:03 2023

@author: dale
"""

from sqlalchemy import Column, BigInteger, Text, Boolean, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import ARRAY
from db.base_class import Base


class Concentrate(Base):
    __table_args__ = {"schema": "public"}

    cultivator = Column(Text, nullable=False)
    strain = Column(Text, nullable=False)
    card_path = Column(Text, nullable=True)
    voting_open = Column(
        Boolean,
        default=True,
        nullable=False,
    )
    concentrate_id = Column(
        BigInteger, primary_key=True, index=True, autoincrement="auto", nullable=False
    )
    is_mystery = Column(
        Boolean,
        default=True,
    )


class Concentrate_Description(Base):
    __table_args__ = {"schema": "public"}
    description_id = Column(BigInteger, primary_key=True, autoincrement=True)
    concentrate_id = Column(
        BigInteger,
        ForeignKey("public.concentrate.concentrate_id", onupdate="CASCADE"),
        nullable=True,
    )
    description = Column(Text, nullable=False, default="Coming Soon", server_default="Coming Soon")
    effects = Column(Text, nullable=False, default="Coming Soon", server_default="Coming Soon")
    lineage = Column(Text, nullable=False, default="Coming Soon", server_default="Coming Soon")
    terpenes_list = Column(ARRAY(Text), nullable=True)
    cultivar_email = Column(Text, ForeignKey("mysteryvoter.email"), nullable=False)

    __table_args__ = (
        CheckConstraint(
            "length(description) < 1500", name="concentrate_descriptions_description_check"
        ),
        CheckConstraint("length(effects) < 1500", name="concentrate_descriptions_effects_check"),
        CheckConstraint("length(lineage) < 1500", name="concentrate_descriptions_lineage_check"),
    )
