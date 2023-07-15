#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 10 21:12:40 2023

@author: dale
"""

from fastapi import APIRouter
from sqlalchemy.orm import Session
from fastapi import Depends

from schemas.users import UserCreate, UserLogin, ShowUser
from db.session import get_supa_db
from db.repository.users import create_new_user
from db._supabase.connect_to_auth import SupaAuth
from gotrue.errors import AuthApiError

router = APIRouter()


@router.post("/", response_model=ShowUser)
def create_user(
        user: UserCreate,
        db: Session = Depends(get_supa_db)
    ):
    user = create_new_user(user=user,db=db)
    return user 
  

@router.post("/", response_model=ShowUser)
def create_supa_user(
    user: UserCreate,
    ) -> SupaAuth:
    try:
        return SupaAuth.create_new_user(user=user)
    except AuthApiError:
        return user


@router.post("/", response_model=ShowUser)
def login_supa_user(
    user: UserLogin,
    ) -> SupaAuth:
    return SupaAuth.login_supabase_user_with_password(user=user)