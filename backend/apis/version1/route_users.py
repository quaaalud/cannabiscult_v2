#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 10 21:12:40 2023

@author: dale
"""

from uuid import UUID
from urllib.parse import urlparse, unquote
from pathlib import Path
from fastapi import APIRouter, Query, BackgroundTasks, Depends, status, HTTPException, Request, Form
from fastapi.responses import RedirectResponse
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
from db._supabase.connect_to_auth import SupaAuth, Client
from gotrue.errors import AuthApiError

router = APIRouter()


templates_dir = Path(
    Path(__file__).parents[2],
    "templates",
)

templates = Jinja2Templates(directory=str(templates_dir))


@router.post("/create_user", response_model=Dict[str, str])
def submit_create_new_user_route(
    user: UserCreate, background_tasks: BackgroundTasks, request: Request, db: Session = Depends(get_db)
):
    background_tasks.add_task(create_new_user, user, db)
    return {"created_user": "completed"}


@router.post("/new_supa_user", response_model=Dict[str, ShowUser])
def create_supa_user(user: UserCreate) -> SupaAuth:
    try:
        return SupaAuth.create_new_supabase_user(user=user)
    except AuthApiError:
        return {"created_user": user}


@router.post("/", response_model=Dict[str, bool])
def login_supa_user(user: UserLogin) -> Dict[str, bool]:
    try:
        logged_in_user = SupaAuth.login_supabase_user_with_password(user=user)
        return {"logged_in_user": True if logged_in_user else False}
    except Exception:
        {"logged_in_user": False}


@router.post(
    "/update_password", response_model=Dict[str, str], dependencies=[Depends(settings.jwt_auth_dependency)]
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
    return {"current_user_profile": "success" if user else "fail"}


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


@router.post("/callback/google")
async def google_auth_callback(request: Request, db: Session = Depends(get_db)):
    try:
        payload = await request.json()
        access_token = payload.get("access_token")
        refresh_token = payload.get("refresh_token")
        if not access_token or not refresh_token:
            raise HTTPException(status_code=400, detail="Missing tokens")
        SupaAuth._client.auth.set_session(access_token, refresh_token)
        session_data = SupaAuth.get_existing_session()
        if not session_data or not session_data.user:
            return RedirectResponse(url="/login", status_code=302)
        user_info = session_data.user
        email = user_info.email
        auth_id = user_info.id
        full_name = user_info.user_metadata.get("full_name", "")
        user = await get_user_by_email(email, db)
        if user:
            if not user.auth_id:
                user.auth_id = auth_id
                db.commit()
        else:
            new_user_data = UserCreate(
                username=email.split('@')[0],
                email=email,
                name=full_name,
                password="",
                auth_id=auth_id,
                phone="",
                zip_code=""
            )
            create_new_user(new_user_data, db)
    except Exception:
        return RedirectResponse(url="/login", status_code=302)
    else:
        raw = request.query_params.get("return_to", "")
        return_to = unquote(raw) if raw else "/home"
        path = urlparse(return_to).path
        if path in ("/login", "/register"):
            return_to = "/home"
        return RedirectResponse(url=return_to, status_code=status.HTTP_302_FOUND)


def _check_for_google_identity(supabase: Client) -> bool:
    response = supabase.auth.get_user_identities()
    google_identity = next((identity for identity in response.identities if identity.provider == 'google'), None)
    return True if google_identity else False
