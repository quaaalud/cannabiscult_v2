#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep  4 17:05:29 2023

@author: dale
"""

from sqlalchemy import Column, Integer, String, Float, ARRAY, BigInteger
from db.base_class import Base



class ConcentrateReview(Base):
    __table_args__ = {'schema': 'public'}

    id = Column(
        BigInteger,
        primary_key=True,
        index=True,
        autoincrement="auto",
        nullable=False
    )
    cultivator = Column(
        String,
        nullable=False
    )
    strain = Column(
        String,
        nullable=False
    )
    overall = Column(
        Float,
        nullable=False
    )
    structure = Column(
        ARRAY(Float),
        nullable=False
    )
    nose = Column(
        ARRAY(Float),
        nullable=False
    )
    flavor = Column(
        ARRAY(Float),
        nullable=False
    )
    effects = Column(
        ARRAY(Float),
        nullable=False
    )
    vote_count = Column(
        Integer,
        nullable=False
    )
    card_path = Column(
        String,
        nullable=True
    )
    terpene_list = Column(
        ARRAY(String),
        nullable=True
    )