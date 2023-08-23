#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Aug 20 21:52:51 2023

@author: dale
"""

from sqlalchemy import Column, String, Float, BigInteger, Date
from db.base_class import Base



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