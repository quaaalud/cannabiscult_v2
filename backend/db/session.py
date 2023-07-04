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

engine = create_engine(settings.DATABASE_URL)

   
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

supa_engine = create_engine(settings.SUPA_URL)
SupaLocal = sessionmaker(
    bind=supa_engine
)


def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()
        
        
def get_supa_db() -> Generator:
    try:
        db = SupaLocal()
        yield db
    finally:
        db.close()
    