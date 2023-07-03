#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 10 19:08:36 2023

@author: dale
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.config import settings
from typing import Generator  

engine = create_engine(settings.SUPA_URL)

   
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()