# -*- coding: utf-8 -*-

from uuid import UUID
from pathlib import Path
from fastapi import APIRouter, Query, BackgroundTasks, Depends, status, HTTPException, Request, Form
from fastapi.templating import Jinja2Templates
from typing import Dict, Any, List, Union, Optional
from sqlalchemy.orm import Session
from schemas.users import (
    EncodedUserEmailSchema,
    ShowUser,
    UserEmailSchema,
    UserIdSchema,
    UserSettingsSchema,
)
from db.session import get_db
from db.repository.users import get_all_users_with_text_enabled
from core.config import settings
from db._supabase.connect_to_auth import SupaAuth, Client
from gotrue.errors import AuthApiError

router = APIRouter()


templates_dir = Path(
    Path(__file__).parents[2],
    "templates",
)

templates = Jinja2Templates(directory=str(templates_dir))


@router.post("/get_texts_enabled", response_model=Optional[List[UserSettingsSchema]])
async def get_all_text_users_route(admin_email: UserEmailSchema = Query(None), db: Session = Depends(get_db)):
    if not admin_email:
        return []
    return [
        UserSettingsSchema.model_validate(user_settings)
        for user_settings in await get_all_users_with_text_enabled(admin_email.email, db)
    ]
