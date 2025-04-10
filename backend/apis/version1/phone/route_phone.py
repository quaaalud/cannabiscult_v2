# -*- coding: utf-8 -*-

from pathlib import Path
from fastapi import APIRouter, Query, Depends, Request, BackgroundTasks
from fastapi.templating import Jinja2Templates
from typing import Any, List
from sqlalchemy.orm import Session
from schemas.users import (
    EncodedUserEmailSchema,
    UserSettingsSchema,
)
from db.session import get_db
from db.repository.users import get_all_users_with_text_enabled
from db.repository.phone import get_new_twilio_messages, bulk_upsert_twilio_messages
from backend.twilio.twilio_base import twilio_client

router = APIRouter()


templates_dir = Path(
    Path(__file__).parents[2],
    "templates",
)

templates = Jinja2Templates(directory=str(templates_dir))


@router.post("/get_texts_enabled_chunked", response_model=Any)
async def get_text_users_chunked(admin_email: EncodedUserEmailSchema = Query(...), db: Session = Depends(get_db)):
    if not admin_email:
        return []
    chunked_results = []
    async for chunks in get_all_users_with_text_enabled(admin_email.email, db):
        chunked_results.extend(UserSettingsSchema.model_validate(chunk) for chunk in chunks)
    return chunked_results


@router.get("/messages/new/", response_model=List[twilio_client.TwilioMessageResultsSchema])
async def get_new_twilio_text_messages_route(
    request: Request, background_tasks: BackgroundTasks, db: Session = Depends(get_db)
):
    new_messages = [
        twilio_client.TwilioMessageResultsSchema.model_validate(message)
        for message in await get_new_twilio_messages(db)
    ]
    background_tasks.add_task(bulk_upsert_twilio_messages, db, new_messages)
    return new_messages
