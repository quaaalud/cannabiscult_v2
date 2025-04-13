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


supa_engine = engine = create_engine(
    settings.SUPA_URL,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800,
    pool_pre_ping=True,
    pool_use_lifo=True,
    connect_args={
        "keepalives": 1,
        "keepalives_idle": 30,
        "keepalives_interval": 10,
        "keepalives_count": 5,
        "options": "-c statement_timeout=5000"
    }
)
SupaLocal = sessionmaker(autocommit=False, autoflush=False, bind=supa_engine)


def get_db() -> Generator:
    try:
        db = SupaLocal()
        yield db
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


get_supa_db = get_db
