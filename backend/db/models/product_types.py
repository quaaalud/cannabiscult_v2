#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov  5 17:09:03 2023

@author: dale
"""

from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import JSONB
from db.base_class import Base


class Product_Types(Base):
    __table_args__ = {"schema": "public"}

    product_type = Column(String, nullable=False, primary_key=True)
    extra_data = Column(JSONB, nullable=True)
