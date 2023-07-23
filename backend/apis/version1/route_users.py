#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 10 21:12:40 2023

@author: dale
"""

from fastapi import APIRouter, Depends
from fastapi import Cookie, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from jose import jwt, JWTError
from schemas.users import UserCreate, UserLogin, ShowUser
from db.session import get_supa_db
from db.repository.users import create_new_user, get_user_by_email
from db._supabase.connect_to_auth import SupaAuth
from core.config import settings
from core.hashing import Hasher
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
        return SupaAuth.create_new_supabase_user(user=user)
    except AuthApiError:
        return user


@router.post("/", response_model=ShowUser)
def login_supa_user(
    user: UserLogin,
    ) -> SupaAuth:
    user.password = Hasher.get_password_hash(user.password)
    print(vars(user))
    logged_in_user = SupaAuth.login_supabase_user_with_password(user=user)
    return logged_in_user


def get_current_user(
    token: Optional[str] = Cookie(None), 
    db: Session = None,
    ):
#    if not token:
#        raise HTTPException(
#            status_code=status.HTTP_401_UNAUTHORIZED,
#            detail="Not authenticated",
#            headers={"WWW-Authenticate": "Bearer"},
#        )
    try:
        payload = jwt.decode(
            token, 
            settings.SUPA_PUBLIC_KEY,
            algorithms=[settings.ALGO]
        )
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        user = get_user_by_email(db=db, email=email)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if not Hasher.verify_password(payload.get("password"), user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
