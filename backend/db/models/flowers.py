#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov  5 17:09:03 2023

@author: dale
"""

from sqlalchemy import Column, String, BigInteger, Boolean
from db.base_class import Base


class Flower(Base):
    __table_args__ = {'schema': 'public'}

    cultivator = Column(
        String,
        nullable=False
    )
    strain = Column(
        String,
        nullable=False
    )
    card_path = Column(
        String,
        nullable=True
    )
    voting_open = Column(
        Boolean,
        default=True,
        nullable=False,
    )
    flower_id = Column(
        BigInteger,
        primary_key=True,
        index=True,
        autoincrement="auto",
        nullable=False
    )
    is_mystery = Column(
        Boolean,
        default=True,
    )
