#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 10 21:13:37 2023

@author: dale
"""

from supabase import Client
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import Union
from schemas.users import (
    UserCreate,
    UserStrainListCreate,
    UserStrainListUpdate,
    UserStrainListSchema,
    UserStrainListRemove,
    AddUserStrainListNotes,
)
from db.models.users import User, UserStrainList
from core.config import settings


@settings.retry_db
def add_user_to_supabase(user: UserCreate, _auth: Client):
    user = User(
        username=user.username,
        email=user.email,
        name=user.name,
        phone=user.phone,
        zip_code=user.zip_code,
        password=user.password,
        agree_tos=True,
        can_vote=False,
        is_superuser=False,
    )
    try:
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
                },
            }
        )
        return res
    except:
        pass


@settings.retry_db
def create_new_user(user: UserCreate, db: Session):
    user = User(
        username=user.username,
        email=user.email,
        name=user.name,
        phone=user.phone,
        zip_code=user.zip_code,
        password=user.password,
        agree_tos=True,
        can_vote=True,
        is_superuser=False,
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


@settings.retry_db
def get_user_by_email(user_email: str, db: Session) -> User:
    user = db.query(User).filter(User.email == user_email).first()
    if user:
        return user
    return None


@settings.retry_db
def get_user_and_update_password(
    user_email: str, username: str, new_password: str, repeated_password: str, db: Session
) -> User:
    if new_password == repeated_password:
        try:
            user = get_user_by_email(user_email, db)
            if user.username == username:
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


@settings.retry_db
async def add_strain_to_list(strain_data: UserStrainListCreate, db: Session):
    strain = (
        db.query(UserStrainList)
        .filter(
            UserStrainList.email == strain_data.email
            and UserStrainList.cultivator == strain_data.cultivator
            and UserStrainList.strain == strain_data.strain
            and UserStrainList.product_type == strain_data.product_type
        )
        .first()
    )
    if strain:
        if strain.strain == strain_data.strain:  # this should not be required but works
            return UserStrainListSchema.from_orm(strain)

    strain = UserStrainList(
        email=strain_data.email,
        strain=strain_data.strain,
        cultivator=strain_data.cultivator,
        to_review=strain_data.to_review,
        product_type=strain_data.product_type,
        strain_notes="",
    )
    try:
        db.add(strain)
    except SQLAlchemyError:
        db.rollback()
        raise
    else:
        db.commit()
        db.refresh(strain)
    return UserStrainListSchema.from_orm(strain)


@settings.retry_db
async def get_strain_list_by_email(user_email: str, db: Session):
    try:
        return [
            UserStrainListSchema.from_orm(strain_list_item)
            for strain_list_item in db.query(UserStrainList)
            .filter(UserStrainList.email == user_email)
            .all()
        ]
    except SQLAlchemyError:
        db.rollback()
        raise


@settings.retry_db
async def update_strain_review_status(
    strain_id: Union[str, int], strain_list_update: UserStrainListUpdate, db: Session
):
    try:
        strain = db.query(UserStrainList).filter(
            UserStrainList.id == int(strain_id)
        ).first()
        strain.to_review = strain_list_update.to_review
        db.commit()
        db.refresh(strain)
    except SQLAlchemyError:
        db.rollback()
        raise
    return UserStrainListSchema.from_orm(strain)


@settings.retry_db
async def add_strain_notes_to_list(strain_notes: AddUserStrainListNotes, db: Session):
    try:
        strain = (
            db.query(UserStrainList)
            .filter(
                UserStrainList.strain == strain_notes.strain
                and UserStrainList.cultivator == strain_notes.cultivator
                and UserStrainList.email == strain_notes.email
                and UserStrainList.product_type == strain_notes.product_type
            )
            .one()
        )
        strain.to_review = strain_notes.to_review
        strain.strain_notes = strain_notes.strain_notes
    except SQLAlchemyError:
        db.rollback()
        raise
    else:
        db.commit()
        db.refresh(strain)
    return UserStrainListSchema.from_orm(strain)


@settings.retry_db
async def delete_strain_from_list(strain_to_remove: UserStrainListRemove, db: Session):
    try:
        strain = (
            db.query(UserStrainList)
            .filter(
                UserStrainList.strain == strain_to_remove.strain
                and UserStrainList.cultivator == strain_to_remove.cultivator
                and UserStrainList.email == strain_to_remove.email
                and UserStrainList.product_type == strain_to_remove.product_type
            )
            .one()
        )
        db.delete(strain)
    except SQLAlchemyError:
        db.rollback()
        raise
    else:
        db.commit()
    return {"data": f"removed {strain_to_remove.strain}"}
