#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 10 21:12:40 2023

@author: dale
"""

from fastapi import APIRouter, Depends
from typing import Dict, Optional, Any
from sqlalchemy.orm import Session
from schemas.users import UserCreate, UserLogin, ShowUser, LoggedInUser
from db.session import get_supa_db
from db.repository.users import create_new_user
from db.repository.users import get_user_by_email
from db.repository.users import get_user_and_update_password
from db._supabase.connect_to_auth import SupaAuth
from gotrue.errors import AuthApiError

router = APIRouter()


@router.post("/", response_model=Dict[str, ShowUser])
def create_user(user: UserCreate, db: Session = Depends(get_supa_db)):
    user = create_new_user(user=user, db=db)
    return {"created_user": user}


@router.post("/", response_model=Dict[str, ShowUser])
def create_supa_user(
    user: UserCreate,
) -> SupaAuth:
    try:
        return SupaAuth.create_new_supabase_user(user=user)
    except AuthApiError:
        return {"created_user": user}


@router.post("/", response_model=Dict[str, LoggedInUser])
def login_supa_user(
    user: UserLogin,
) -> SupaAuth:
    logged_in_user = SupaAuth.login_supabase_user_with_password(user=user)
    return {"logged_in_user": logged_in_user}


@router.post("/update_password", response_model=Dict[str, ShowUser])
def update_user_password(
    user_email: str,
    username: str,
    new_password: str,
    repeated_password: str,
    db: Session = Depends(get_supa_db),
):
    user = get_user_and_update_password(
        user_email=user_email,
        username=username,
        new_password=new_password,
        repeated_password=repeated_password,
        db=db,
    )
    return {"current_user_profile": user}


@router.get("/logout", response_model=None)
def logout_current_user() -> SupaAuth:
    SupaAuth.logout_current_user_session()
    pass


@router.get("/current_user", response_model=Dict[str, Any])
def get_current_users_email() -> SupaAuth:
    current_user_email = SupaAuth.return_current_user_email()
    return {"current_user": current_user_email}


@router.get("/get_current_user", response_model=Dict[str, Any])
async def async_get_current_users_email() -> SupaAuth:
    current_user_email = SupaAuth.return_current_user_email()
    return {"current_user": current_user_email}


@router.get("/voting_status", response_model=Dict[str, Any])
def return_current_user_vote_status(user_email: str, db: Session = Depends(get_supa_db)):
    user = get_user_by_email(user_email=user_email, db=db)
    if user:
        return {"user_vote_status": user.can_vote}
