#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 10 21:13:37 2023

@author: dale
"""


import base64
from uuid import UUID
from supabase import Client
from sqlalchemy import func, delete
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import SQLAlchemyError
from pydantic import ValidationError
from typing import Union, Dict, List, Callable, Awaitable, AsyncGenerator
from schemas.users import (
    UserCreate,
    UserStrainListCreate,
    UserStrainListUpdate,
    UserStrainListSchema,
    UserStrainListRemove,
    AddUserStrainListNotes,
    UserSettingsSchema,
)
from db.base import User, UserStrainList, MoluvHeadstashBowl, UserSettings
from backend.twilio.twilio_base import twilio_client
from core.config import settings


def decode_email(encoded_email: str) -> str:
    return base64.b64decode(encoded_email).decode("utf-8")


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
    except Exception:
        pass


@settings.retry_db
def create_new_user(user: UserCreate, db: Session):
    try:
        existing_user = db.query(User).filter(User.email == user.email).first()
        if existing_user:
            existing_user.username = user.username
            existing_user.name = user.name
            if user.auth_id:
                existing_user.auth_id = user.auth_id
            db.commit()
            db.refresh(existing_user)
            return existing_user
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
            auth_id=user.auth_id,
        )
        db.add(user)
        if user.auth_id:
            default_settings = UserSettings(
                user_id=user.auth_id,
                text_settings={"enabled": "yes"},
                email_settings={"enabled": "yes"},
                site_settings={"dark_mode": "system"},
            )
            db.add(default_settings)
        db.commit()
        return user
    except Exception as e:
        db.rollback()
        raise e


@settings.retry_db
async def get_user_by_user_id(user_id: UUID, db: Session) -> Union[str, None]:
    try:
        if not isinstance(user_id, UUID):
            user_id = UUID(user_id)
        user = db.query(User).filter(User.auth_id == user_id).first()
        return user
    except Exception:
        db.rollback()
        return None


@settings.retry_db
async def get_user_by_email(user_email: str, db: Session) -> User:
    try:
        decoded_email = decode_email(user_email)
        user = db.query(User).filter(User.email == decoded_email).first()
    except Exception:
        db.rollback()
        return None
    return user


@settings.retry_db
async def get_all_users_with_settings(
    db: Session, chunk_size: int = 100, pages: int = None
) -> AsyncGenerator[List[UserSettings], None]:
    offset = 0
    page_count = 0
    while True:
        if pages is not None and page_count >= pages:
            break
        chunk = (
            db.query(UserSettings)
            .options(joinedload(UserSettings.user))
            .join(User, UserSettings.user_id == User.auth_id)
            .limit(chunk_size)
            .offset(offset)
            .all()
        )
        if not chunk:
            break
        yield chunk
        if len(chunk) < chunk_size:
            break

        offset += len(chunk)
        page_count += 1


@settings.retry_db
async def get_all_users_with_text_enabled(
    db: Session, chunk_size: int = 100, pages: int = None
) -> AsyncGenerator[List[UserSettings], None]:
    offset = 0
    page_count = 0
    while True:
        if pages is not None and page_count >= pages:
            break
        chunk = (
            db.query(UserSettings)
            .options(joinedload(UserSettings.user))
            .join(User, UserSettings.user_id == User.auth_id)
            .filter(UserSettings.text_settings["enabled"].astext == "yes")
            .limit(chunk_size)
            .offset(offset)
            .all()
        )
        if not chunk:
            break
        yield chunk
        if len(chunk) < chunk_size:
            break
        offset += len(chunk)
        page_count += 1


@settings.retry_db
async def get_all_users_with_email_enabled(
    db: Session, chunk_size: int = 100, pages: int = None
) -> AsyncGenerator[List[UserSettings], None]:
    offset = 0
    page_count = 0
    while True:
        if pages is not None and page_count >= pages:
            break
        chunk = (
            db.query(UserSettings)
            .options(joinedload(UserSettings.user))
            .join(User, UserSettings.user_id == User.auth_id)
            .filter(UserSettings.email_settings["enabled"].astext == "yes")
            .limit(chunk_size)
            .offset(offset)
            .all()
        )
        if not chunk:
            break
        yield chunk
        if len(chunk) < chunk_size:
            break
        offset += len(chunk)
        page_count += 1


async def process_action_based_on_user_settings(
    generator_func: Callable[..., AsyncGenerator[List[UserSettings], None]],
    db: Session,
    action: Callable[[UserSettingsSchema], Awaitable[None]],
    chunk_size: int = 100,
    pages: int = None,
) -> None:
    sent_numbers = set()
    try:
        async for chunk in generator_func(db=db, chunk_size=chunk_size, pages=pages):
            for record in chunk:
                validated_record = UserSettingsSchema.model_validate(record)
                try:
                    user_phone = twilio_client.TwilioPhoneNumberSchema.validate(
                        {"phone_number": validated_record.user.phone}
                    ).phone_number
                except ValidationError:
                    continue
                else:
                    if user_phone not in sent_numbers:
                        await action(validated_record)
                        sent_numbers.add(user_phone)
    except SQLAlchemyError:
        db.rollback()
    else:
        db.commit()
    finally:
        sent_numbers = set()


@settings.retry_db
def update_user_password_in_db(user_email: str, new_password: str, repeated_password: str, db: Session) -> User:
    if new_password.strip() == repeated_password.strip():
        raise ValueError("Password values did not match.")
    try:
        user = db.query(User).filter(User.email == user_email.lower().strip()).first()
        if not user:
            return None
        user.password = new_password
        db.commit()
        db.refresh(user)
        return user
    except SQLAlchemyError as se:
        db.rollback()
        raise se


@settings.retry_db
async def add_strain_to_list(strain_data: UserStrainListCreate, db: Session):
    stmt = insert(UserStrainList).values(
        email=strain_data.email,
        strain=strain_data.strain,
        cultivator=strain_data.cultivator,
        to_review=strain_data.to_review,
        product_type=strain_data.product_type,
        strain_notes="",
    )
    stmt = stmt.on_conflict_do_update(
        index_elements=["email", "strain", "cultivator", "product_type"], set_={"to_review": strain_data.to_review}
    ).returning(UserStrainList)
    try:
        result = db.execute(stmt)
        upserted_record = result.scalar_one()
    except SQLAlchemyError:
        db.rollback()
        raise
    else:
        db.commit()
    return UserStrainListSchema.from_orm(upserted_record)


@settings.retry_db
async def get_strain_list_by_email(user_email: str, db: Session):
    try:
        return [
            UserStrainListSchema.from_orm(strain_list_item)
            for strain_list_item in db.query(UserStrainList).filter(UserStrainList.email == user_email).all()
        ]
    except SQLAlchemyError:
        db.rollback()
        raise


@settings.retry_db
async def update_strain_review_status(
    strain_id: Union[str, int], strain_list_update: UserStrainListUpdate, db: Session
):
    try:
        strain = db.query(UserStrainList).filter(UserStrainList.id == int(strain_id)).first()
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
        stmt = delete(UserStrainList).where(
            UserStrainList.strain.ilike(f"%{strain_to_remove.strain}%"),
            UserStrainList.cultivator.ilike(f"%{strain_to_remove.cultivator}"),
            UserStrainList.email == strain_to_remove.email,
            UserStrainList.product_type == strain_to_remove.product_type.lower(),
        )
        result = db.execute(stmt)
    except SQLAlchemyError:
        db.rollback()
        raise
    else:
        db.commit()
    return {"data": f"removed {result.rowcount} record(s)"}


@settings.retry_db
async def upsert_moluv_headstash_vote(db: Session, user_id: UUID, product_type: str, product_id: int) -> Dict[str, str]:
    try:
        stmt = insert(MoluvHeadstashBowl).values(
            user_id=user_id,
            product_type=product_type,
            product_id=product_id,
        )
        stmt = stmt.on_conflict_do_update(
            constraint="uq_user_product", set_={"product_id": product_id, "updated_at": func.now()}
        )
        db.execute(stmt)
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        raise e
    return {"product_type": product_type, "product_id": str(product_id)}
