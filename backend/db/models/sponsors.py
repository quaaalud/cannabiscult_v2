#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 10 19:17:20 2023

@author: dale
"""

from sqlalchemy import Column, Integer, String, Boolean,Date#, ForeignKey
#from sqlalchemy.orm import relationship

from db.base_class import Base


class Sponsors(Base):
    id = Column(
        Integer,
        primary_key=True,
        index=True
    )
    product = Column(
        String,
        nullable=False
    )
    company = Column(
        String,
        nullable=False
    )
    company_url = Column(
        String,
        nullable=False,
    )
    address = Column(
        String,
        nullable=False
    )
    description = Column(
        String,
        nullable=False
    )
    date_posted = Column(Date)
    is_active = Column(
        Boolean(),
        default=True
    )
    