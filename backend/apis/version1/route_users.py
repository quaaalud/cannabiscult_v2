#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 10 21:12:40 2023

@author: dale
"""

from fastapi import APIRouter
from sqlalchemy.orm import Session
from fastapi import Depends

from schemas.users import UserCreate, ShowUser
from db.session import get_db
from db.repository.users import create_new_user

router = APIRouter()


@router.post("/", response_model=ShowUser)
def create_user(
        user: UserCreate,
        db: Session = Depends(get_db)
    ):
    user = create_new_user(user=user,db=db)
    return user 
