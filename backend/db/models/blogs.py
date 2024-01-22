#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr 15 19:17:33 2023

@author: dale
"""

from sqlalchemy import Column, Integer, String, Boolean, Date

from db.base_class import Base


class Blogs(Base):
    id = Column(
        Integer,
        primary_key=True,
        index=True
    )
    title = Column(
        String,
        nullable=False
    )
    description = Column(
        String,
        nullable=False
    )
    url = Column(
        String,
        nullable=False,
    )
    creative_name = Column(
        String,
        nullable=False
    )
    author = Column(
        String,
        nullable=False
    )
    date_posted = Column(
        Date
    )
    is_active = Column(
        Boolean(),
        default=True
    )
