#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 10 21:13:37 2023

@author: dale
"""

from sqlalchemy.orm import Session
from schemas.users import UserCreate
from db.models.users import User
from core.hashing import Hasher


def create_new_user(user:UserCreate,db:Session):
    user = User(
        username=user.username,
        email = user.email,
        hashed_password=Hasher.get_password_hash(user.password),
        is_active=True,
        is_superuser=False
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
