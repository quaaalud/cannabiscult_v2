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


supa_engine = engine = create_engine(settings.SUPA_URL)
SupaLocal = sessionmaker(autocommit=False, autoflush=False, bind=supa_engine)


def get_db() -> Generator:
    try:
        db = SupaLocal()
        yield db
    except Exception:
        db.rollback()
    finally:
        db.close()


get_supa_db = get_db
