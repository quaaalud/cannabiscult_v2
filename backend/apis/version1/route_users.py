#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 10 21:12:40 2023

@author: dale
"""

from uuid import UUID
from pathlib import Path
from fastapi import APIRouter, Query, BackgroundTasks, Depends, status, HTTPException, Request, Form
from fastapi.templating import Jinja2Templates
from typing import Dict, Any, List, Union, Optional
from sqlalchemy.orm import Session
from schemas.users import (
    EncodedUserEmailSchema,
    UserCreate,
    UserLogin,
    ShowUser,
    UserEmailSchema,
    UserStrainListSchema,
    UserStrainListCreate,
    UserStrainListUpdate,
    UserStrainListSubmit,
    AddUserStrainListNotes,
    UserIdSchema,
    MoluvHeadstashFavoriteVoteSchema,
    MoluvHeadstashFavoriteVoteResult,
)
from db.session import get_db
from db.repository.users import (
    create_new_user,
    get_user_by_user_id,
    get_user_by_email,
    update_user_password_in_db,
    add_strain_to_list,
    get_strain_list_by_email,
    update_strain_review_status,
    add_strain_notes_to_list,
    delete_strain_from_list,
    upsert_moluv_headstash_vote,
)
from core.config import settings
from db._supabase.connect_to_auth import SupaAuth
from gotrue.errors import AuthApiError

router = APIRouter()


templates_dir = Path(
    Path(__file__).parents[2],
    "templates",
)

templates = Jinja2Templates(directory=str(templates_dir))


@router.post("/create_user", response_model=Dict[str, ShowUser])
def submit_create_new_user_route(
    user: UserCreate, background_tasks: BackgroundTasks, request: Request, db: Session = Depends(get_db)
):
    background_tasks.add_task(create_new_user, user, db)
    return {"created_user": user}


@router.post("/new_supa_user", response_model=Dict[str, ShowUser])
def create_supa_user(user: UserCreate) -> SupaAuth:
    try:
        return SupaAuth.create_new_supabase_user(user=user)
    except AuthApiError:
        return {"created_user": user}


@router.post("/", response_model=Dict[str, bool])
def login_supa_user(user: UserLogin) -> Dict[str, bool]:
    logged_in_user = SupaAuth.login_supabase_user_with_password(user=user)
    return {"logged_in_user": True if logged_in_user else False}


@router.post(
    "/update_password", response_model=Dict[str, ShowUser], dependencies=[Depends(settings.jwt_auth_dependency)]
)
def update_user_password(
    request: Request,
    user_email: str = Form(...),
    new_password: str = Form(...),
    repeated_password: str = Form(...),
    db: Session = Depends(get_db),
):
    user = update_user_password_in_db(
        user_email=user_email,
        new_password=new_password,
        repeated_password=repeated_password,
        db=db,
    )
    return {"current_user_profile": ShowUser.from_orm(user)}


@router.get("/logout/", response_model=None)
def logout_current_user() -> SupaAuth:
    try:
        SupaAuth.logout_current_user_session()
    except AuthApiError:
        pass
    return


@router.get("/current_user", response_model=Dict[str, Any])
def get_current_users_email() -> SupaAuth:
    try:
        current_user_email = SupaAuth.return_current_user_email()
    except Exception:
        current_user_email = None
    return {"current_user": current_user_email}


@router.get("/get_current_user", response_model=Dict[str, Any])
async def async_get_current_users_email() -> SupaAuth:
    try:
        current_user_email = SupaAuth.return_current_user_email()
    except Exception:
        current_user_email = None
    return {"current_user": current_user_email}


@router.get("/get_user_by_id", response_model=Optional[ShowUser])
async def async_get_user_by_id(
    user_id: UUID = Query(..., description="UUID of the user"), db: Session = Depends(get_db)
):
    try:
        user = await get_user_by_user_id(user_id, db)
    except Exception:
        user = None
    return user


@router.post("/get_username", response_model=Optional[Dict[str, Any]])
async def return_username_by_email(user_email: EncodedUserEmailSchema, db: Session = Depends(get_db)):
    user = await get_user_by_email(user_email=user_email.email, db=db)
    if user:
        return {"username": user.username}


@router.post("/super_user_status", response_model=Dict[str, Any])
async def return_is_superuser_status(user_id: UserIdSchema, db: Session = Depends(get_db)):
    user = await get_user_by_user_id(user_id.user_id, db)
    if user:
        return {"supuser_status": user.is_superuser}
    return {"supuser_status": False}


@router.post(
    "/add_strain_to_list",
    response_model=UserStrainListSchema,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(settings.jwt_auth_dependency)],
)
async def add_strain_to_user_list(
    strain_data: UserStrainListCreate,
    db: Session = Depends(get_db),
):
    try:
        return await add_strain_to_list(strain_data, db)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/my_strains/", response_model=List[UserStrainListSchema], dependencies=[Depends(settings.jwt_auth_dependency)]
)
async def get_strains_by_email(user_email_schema: UserEmailSchema, db: Session = Depends(get_db)):
    try:
        strains = await get_strain_list_by_email(user_email_schema.email, db)
        if strains is None:
            raise HTTPException(status_code=404, detail="Strains not found")
        return strains
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch(
    "/update_strain_list/{strain_id}",
    response_model=UserStrainListSubmit,
    dependencies=[Depends(settings.jwt_auth_dependency)],
)
async def update_strain_status(
    strain_id: Union[str, int],
    update_data: UserStrainListUpdate,
    db: Session = Depends(get_db),
):
    try:
        updated_strain = await update_strain_review_status(strain_id, update_data, db)
        if updated_strain is None:
            raise HTTPException(status_code=404, detail="Strain not found")
        return updated_strain
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch(
    "/update_strain_notes/", response_model=UserStrainListSubmit, dependencies=[Depends(settings.jwt_auth_dependency)]
)
async def update_strain_notes(strain_notes: AddUserStrainListNotes, db: Session = Depends(get_db)):
    try:
        updated_strain = await add_strain_notes_to_list(strain_notes, db)
        if updated_strain is None:
            raise HTTPException(status_code=404, detail="Strain not found")
        return updated_strain
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete(
    "/delete_strain_from_list/",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(settings.jwt_auth_dependency)],
)
async def delete_strain_from_strain_list(strain_to_remove: UserStrainListCreate, db: Session = Depends(get_db)):
    try:
        await delete_strain_from_list(strain_to_remove, db)
        return {"message": "Strain deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post(
    "/moluv/favorite/",
    response_model=MoluvHeadstashFavoriteVoteResult,
    dependencies=[Depends(settings.jwt_auth_dependency)]
)
async def upsert_moluv_headstash_vote_route(
    request: Request,
    moluv_vote: MoluvHeadstashFavoriteVoteSchema,
    db: Session = Depends(get_db),
) -> MoluvHeadstashFavoriteVoteResult:
    try:
        result = await upsert_moluv_headstash_vote(
            db,
            moluv_vote.user_id,
            moluv_vote.product_type,
            moluv_vote.product_id
        )
        if not result:
            raise HTTPException(status_code=400, detail="No result returned for Moluv collab favorite vote.")
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/callback/google", response_model=Dict[str, str])
async def google_auth_callback(request: Request, db: Session = Depends(get_db)):
    try:
        session_data = SupaAuth.get_existing_session()
    except Exception:
        session_data = None
    if not session_data:
        return {"status": "failure", "message": "User failed to authenticate with Google OAuth"}
    email = session_data.user.email
    google_auth_id = session_data.user.id
    user = await get_user_by_email(email, db)
    if user:
        if not user.auth_id:
            user.auth_id = google_auth_id
            db.commit()
    else:
        new_user_data = UserCreate(
            username=email.split('@')[0],
            email=email,
            name=session_data.user.user_metadata.get("full_name", ""),
            password="",
            auth_id=google_auth_id,
            phone="",
            zip_code=""
        )
        user = create_new_user(new_user_data, db)
    return {"status": "success", "message": "User authenticated via Google OAuth"}
