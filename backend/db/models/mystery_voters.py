#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 11 21:48:19 2023

@author: dale
"""

from sqlalchemy import Column, Integer, String, Boolean, Date

from db.base_class import Base


class MysteryVoter(Base):
    id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement="auto",
    )
    email = Column(
        String,
        nullable=False,
        unique=True,
        index=True
    )
    name = Column(
        String,
        nullable=True,
        unique=False,
    )
    zip_code = Column(
        String,
        nullable=True,
        unique=False,
    )
    phone = Column(
        String,
        nullable=True,
        unique=False,
    )
    agree_tos = Column(
        Boolean(),
        default=True
    )
    date_posted = Column(
        Date
    )