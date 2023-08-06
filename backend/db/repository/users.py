#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 10 21:13:37 2023

@author: dale
"""

from supabase import Client
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from schemas.users import UserCreate
from db.models.users import User
#from core.hashing import Hasher


def add_user_to_supabase(user:UserCreate, _auth:Client):
    user = User(
        username= user.username,
        email= user.email,
        name = user.name,
        phone = user.phone,
        zip_code = user.zip_code,
        password = user.password,
        agree_tos = True,
        can_vote = False,
        is_superuser = False

    )
    res = _auth.auth.sign_up(
        {
            "email": user.email,
            "password": user.password,
            "options": {
                "data": {
                    "username": user.username,
                    "name": user.name,
                    "zip_code": user.zip_code,
                    "agree_tos": user.agree_tos,
                    "phone": user.phone,
                    "can_vote": user.can_vote,
                    "is_superuser": user.is_superuser,
                }
            }
        }
    )
    return res


def create_new_user(user:UserCreate, db:Session):
    user = User(
        username= user.username,
        email= user.email,
        name = user.name,
        phone = user.phone,
        zip_code = user.zip_code,
        password = user.password,
        agree_tos = True,
        can_vote = False,
        is_superuser = False

    )
    try:
        db.add(user)
    except:
        db.rollback()
    else:
        db.commit()
        db.refresh(user)
    finally:
        return user
      
      
def get_user_by_email(
        user_email: str,
        db: Session) -> User:
    user = db.query(
        User
    ).filter(User.email == user_email).first()
    if user:
        return user
      
      
def get_user_and_update_password(
    user_email: str,
    current_password: str,
    new_password: str,
    repeated_password: str,
    db: Session) -> User:
    if new_password == repeated_password:
        try:
            user = get_user_by_email(user_email, db)
            if user.password  == current_password:
                user.password = new_password
            else:
                raise SQLAlchemyError
        except SQLAlchemyError:
            db.rollback()
        else:
            db.commit()
            db.refresh(user)
        finally:
            return user
    else:
        return None
      