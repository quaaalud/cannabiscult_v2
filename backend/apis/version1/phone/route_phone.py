# -*- coding: utf-8 -*-

from pathlib import Path
from fastapi import APIRouter, Query, Depends, Request, BackgroundTasks
from fastapi.templating import Jinja2Templates
from functools import partial
from typing import Any
from pydantic import ValidationError
from sqlalchemy.orm import Session
from schemas.users import (
    EncodedUserEmailSchema,
    UserSettingsSchema,
)
from db.session import get_db
from db.repository.users import get_all_users_with_text_enabled, process_action_based_on_user_settings
from db.repository.phone import get_new_twilio_messages, bulk_upsert_twilio_messages, upsert_twilio_message
from backend.twilio.twilio_base import twilio_client
from backend.core.config import settings

router = APIRouter()


templates_dir = Path(
    Path(__file__).parents[2],
    "templates",
)

templates = Jinja2Templates(directory=str(templates_dir))


async def send_text_action(record: UserSettingsSchema, template_id: str, db: Session) -> None:
    try:
        user_data = {
            "phone": twilio_client.TwilioPhoneNumberSchema.validate({"phone_number": record.user.phone}).phone_number,
            "username": record.user.username,
        }
    except ValidationError:
        return
    else:
        message = await twilio_client.send_sms_content_template(template_id, user_data)
        await upsert_twilio_message(db, twilio_client.TwilioMessageResultsSchema.model_validate(message).dict())
        # print(f"Sending text to user {user_data['username']} with phone: {user_data['phone']}")


@router.post(
    "/get_texts_enabled_chunked", response_model=Any, dependencies=[Depends(settings.jwt_admin_auth_dependency)]
)
async def get_text_users_chunked(db: Session = Depends(get_db)):
    chunked_results = []
    async for chunks in get_all_users_with_text_enabled(db):
        chunked_results.extend(UserSettingsSchema.model_validate(chunk) for chunk in chunks)
    return chunked_results


@router.post("/send_texts/{template_id}/all", dependencies=[Depends(settings.jwt_admin_auth_dependency)])
async def send_mass_text_message_template_route(
    request: Request,
    template_id: str,
    db: Session = Depends(get_db),
):
    action_with_template = partial(send_text_action, template_id=template_id, db=db)
    await process_action_based_on_user_settings(
        generator_func=get_all_users_with_text_enabled,
        db=db,
        action=action_with_template,
        chunk_size=500,
        pages=None,
    )


@router.get("/messages/new/", response_model=None, dependencies=[Depends(settings.jwt_admin_auth_dependency)])
async def get_new_twilio_text_messages_route(
    request: Request, background_tasks: BackgroundTasks, db: Session = Depends(get_db)
):
    new_messages = [
        twilio_client.TwilioMessageResultsSchema.model_validate(message)
        for message in await get_new_twilio_messages(db)
    ]
    background_tasks.add_task(bulk_upsert_twilio_messages, db, new_messages)
    return


@router.get("/cancel/{message_id}", dependencies=[Depends(settings.jwt_admin_auth_dependency)])
async def camcel_queued_message(message_id: str, db: Session = Depends(get_db)):
    message = await twilio_client.cancel_queued_message(message_id)
    await upsert_twilio_message(db, twilio_client.TwilioMessageResultsSchema.model_validate(message).dict())
