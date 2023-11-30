#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov  5 17:09:03 2023

@author: dale
"""

from sqlalchemy import Column, BigInteger, Text, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.sql import func
from db.base_class import Base


class Concentrate(Base):
    __table_args__ = {'schema': 'public'}

    cultivator = Column(
        Text,
        nullable=False
    )
    strain = Column(
        Text,
        nullable=False
    )
    card_path = Column(
        Text,
        nullable=True
    )
    voting_open = Column(
        Boolean,
        default=True,
        nullable=False,
    )
    concentrate_id = Column(
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
