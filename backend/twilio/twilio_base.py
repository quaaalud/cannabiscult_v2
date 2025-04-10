#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr  9 15:55:39 2025

@author: dale
"""

import sys
from pathlib import Path
import aiohttp
from uuid import UUID
from aiohttp import BasicAuth
from zoneinfo import ZoneInfo
import twilio
from twilio.rest import Client
from twilio.http.async_http_client import AsyncTwilioHttpClient
from datetime import datetime, timedelta
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional

try:
    from backend.core.config import settings
except ModuleNotFoundError:
    sys.path.append(str(Path(__file__).parents[3]))
    from backend.core.config import settings


class TwilioMessageSchema(BaseModel):
    from_: str
    to: str
    body: str
    body_hash: Optional[str] = Field(None, example="Hello, this is a test message.")
    status: str = Field("new", example="processed")
    sid: Optional[str] = Field(None, example="SMa47c8588b20a7444f888880f82288df86")
    created_at: datetime = Field(None, example="2024-07-01T15:30:00")
    date_sent: Optional[datetime] = Field(None, example="2024-07-01T15:30:00")
    send_at: Optional[datetime] = Field(None, example="2024-07-01T15:30:00")

    @field_validator("created_at", mode="before")
    def set_created_at(cls, v):
        return v or datetime.now()

    @field_validator("from_", "to", mode="before")
    def validate_and_format_phone_number(cls, v):
        v = "".join(filter(str.isdigit, v))
        if not v.startswith("1"):
            v = f"1{v}"
        if len(v) != 11:
            raise ValueError("Phone number must be 10 digits long after adding the +1 prefix")
        return f"+{v}"

    class Config:
        from_attributes = True
        populate_by_name = True
        strip_whitespace = True


class TwilioTextMessageSendSchema(BaseModel):
    from_phone: str = Field(..., example="3146288234")
    to_phone_number: str = Field(..., example="3146610066")
    message_body: str = Field(..., example="Hello, this is a test message.")

    @field_validator("from_phone", "to_phone_number", mode="before")
    def validate_and_format_phone_number(cls, v):
        v = "".join(filter(str.isdigit, v))
        if not v.startswith("1"):
            v = f"1{v}"
        if len(v) != 11:
            raise ValueError("Phone number must be 10 digits long after adding the +1 prefix")
        return f"+{v}"


class TwilioMMSMessageSendSchema(BaseModel):
    from_phone: str = Field(..., example="3146288234")
    to_phone_number: str = Field(..., example="3146610066")
    message_body: str = Field(..., example="Hello, this is a test message.")
    attachment_uri: str = Field(..., example="https://cannabiscult.co/")

    @field_validator("from_phone", "to_phone_number", mode="before")
    def validate_and_format_phone_number(cls, v):
        v = "".join(filter(str.isdigit, v))
        if not v.startswith("1"):
            v = f"1{v}"
        if len(v) != 11:
            raise ValueError("Phone number must be 10 digits long after adding the +1 prefix")
        return f"+{v}"


class TwilioScheduledMessageSchema(BaseModel):
    id: Optional[UUID] = Field(None, example="c5d95b6d-65e7-4ab8-9c96-f0437393b22d")
    from_phone: Optional[str] = Field(None, example="+13146288234")
    to_phone_number: str = Field(..., example="+13146610066")
    message_body: str = Field(..., example="This is a scheduled message.")
    send_at: datetime = Field(..., example="2024-07-01T15:30:00")
    schedule_type: str = Field("fixed", example="fixed")
    sid: Optional[str] = Field(None, example="SMa47c8588b20a7444f888880f82288df86")
    created_at: datetime = Field(None, example="2024-07-01T15:30:00")
    date_sent: Optional[datetime] = Field(None, example="2024-07-01T15:30:00")

    @field_validator("created_at", mode="before")
    def set_created_at(cls, v):
        return v or datetime.now()

    @field_validator("send_at", mode="before")
    def updated_send_at_to_utc(cls, v):
        cst_zone = ZoneInfo("America/Chicago")
        now_cst = datetime.now(tz=cst_zone)
        min_cst = now_cst + timedelta(minutes=15)
        if isinstance(v, str):
            try:
                naive_dt = datetime.strptime(v, "%Y-%m-%dT%H:%M")
                v_cst = naive_dt.replace(tzinfo=cst_zone)
            except ValueError:
                v_cst = min_cst
        elif isinstance(v, datetime):
            if v.tzinfo is None:
                v_cst = v.replace(tzinfo=cst_zone)
            else:
                v_cst = v.astimezone(cst_zone)
        else:
            v_cst = min_cst
        if v_cst < min_cst:
            v_cst = min_cst
        start_of_day = v_cst.replace(hour=8, minute=0, second=0, microsecond=0)
        end_of_day = v_cst.replace(hour=21, minute=0, second=0, microsecond=0)
        if v_cst < start_of_day:
            v_cst = start_of_day
        if v_cst >= end_of_day:
            v_cst = start_of_day + timedelta(days=1)
        return v_cst.astimezone(ZoneInfo("UTC"))

    @field_validator("from_phone", "to_phone_number", mode="before")
    def validate_and_format_phone_number(cls, v):
        if not isinstance(v, str):
            raise ValueError("Phone number must be a string.")
        v = "".join(filter(str.isdigit, v))
        if not v.startswith("1"):
            v = f"1{v}"
        if len(v) != 11:
            raise ValueError("Phone number must be 10 digits long after adding the +1 prefix.")
        return f"+{v}"

    @field_validator("schedule_type")
    def validate_schedule_type(cls, v):
        valid_types = {"fixed"}  # Add other valid types if needed
        if v not in valid_types:
            raise ValueError(f"schedule_type must be one of {valid_types}.")
        return v

    class Config:
        from_attributes = True
        populate_by_name = True
        strip_whitespace = True


class TwilioPhoneNumberSchema(BaseModel):
    phone_number: str = Field(..., example="3146288031")

    @field_validator("phone_number", mode="before")
    def validate_and_format_phone_number(cls, v):
        if not isinstance(v, str):
            raise ValueError("Phone number must be a string.")
        v = "".join(filter(str.isdigit, v))
        if not v.startswith("1"):
            v = f"1{v}"
        if len(v) != 11:
            raise ValueError("Phone number must be 10 digits long after adding the +1 prefix.")
        return f"+{v}"

    class Config:
        from_attributes = True
        populate_by_name = True
        strip_whitespace = True
        exclude_unset = True


class TwilioClient:
    _http_client: AsyncTwilioHttpClient = None
    _client: Client = None

    _sid: str = settings.twilio_sid
    _sid: str = settings.twilio_token
    _mid: str = settings.twilio_primary_mid

    _marketing_mid: str = settings.twilio_marketing_mid

    twilio_api_sid: str = settings.twilio_api_sid
    twilio_api_secret: str = settings.twilio_api_secret

    twilio_test_sid: str = settings.twilio_test_sid
    twilio_test_token: str = settings.twilio_test_token

    twilio_local_phone: str = settings.twilio_local_phone
    twilio_toll_free_phone: str = settings.twilio_toll_free_phone

    TwilioMessageSchema = TwilioMessageSchema
    TwilioTextMessageSendSchema = TwilioTextMessageSendSchema
    TwilioMMSMessageSendSchema = TwilioMMSMessageSendSchema
    TwilioScheduledMessageSchema = TwilioScheduledMessageSchema
    TwilioPhoneNumberSchema = TwilioPhoneNumberSchema

    def __init__(self):
        pass

    @staticmethod
    def return_e164_phone_formatting(phone_str: str) -> str | None:
        if not isinstance(phone_str, str):
            return None
        v = "".join(filter(str.isdigit, phone_str))
        if not v.startswith("1"):
            v = f"1{v}"
        if len(v) != 11:
            raise ValueError("Phone number must be 10 digits long after adding the +1 prefix")
        return f"+{v}"

    @classmethod
    async def _return_authenticated_twilio_client(cls, is_dev: bool = False):
        # Need to implement check for development to use 800 number and test credentials
        try:
            if not cls._http_client:
                cls._http_client = AsyncTwilioHttpClient()
            if not cls._client:
                cls._client = Client(cls._sid, cls._key, http_client=cls._http_client)
        except twilio.base.exceptions.TwilioException:
            pass
        return cls._client

    @classmethod
    async def _get_all_messages(
        cls, to_phone_number: str = None, newest_message_date: Optional[datetime] = None
    ) -> List:
        client = await cls._return_authenticated_twilio_client()
        newest_message_date = newest_message_date if newest_message_date else datetime(2025, 1, 1)
        received_messages = await client.api.messages.list_async(
            to=to_phone_number,
            date_sent_after=newest_message_date,
        )
        future_messages = await client.api.messages.list_async(
            from_=to_phone_number,
        )
        validated_future_messages = [
            message
            for message in future_messages
            if (
                to_phone_number == message.from_
                and (message.sid is not None and message.date_sent is None and message.status != "canceled")
            )
        ]
        return [*validated_future_messages, *received_messages]

    async def _send_twilio_text_message(
        self, message_body, to_phone: str = "+13146610066", from_phone: Optional[str] = None
    ):
        if not await self._verify_valid_mobile_phone(to_phone):
            return None
        from_phone = from_phone if from_phone else self.twilio_local_phone
        client = await self._return_authenticated_twilio_client()
        return await client.messages.create_async(from_=from_phone, body=message_body, to=to_phone)

    async def _send_twilio_mms_message(
        self,
        message_body,
        to_phone: str = "+13146610066",
        from_phone: Optional[str] = None,
        attachment_uri: str = None,
    ):
        if not await self._verify_valid_mobile_phone(to_phone):
            return None
        from_phone = from_phone if from_phone else self.twilio_local_phone
        client = await self._return_authenticated_twilio_client()
        return await client.messages.create_async(
            from_=from_phone, body=message_body, to=to_phone, media_url=[attachment_uri]
        )

    async def _schedule_twilio_text_message(
        self, scheduled_message_data: TwilioScheduledMessageSchema, is_marketing: bool = False
    ) -> Client.messages:
        if not await self._verify_valid_mobile_phone(scheduled_message_data.to_phone_number):
            return None
        from_phone = scheduled_message_data.from_phone if scheduled_message_data.from_phone else self.twilio_local_phone
        client = await self._return_authenticated_twilio_client()
        return await client.messages.create_async(
            from_=from_phone,
            body=scheduled_message_data.message_body,
            to=scheduled_message_data.to_phone_number,
            send_at=scheduled_message_data.send_at,
            schedule_type="fixed",
            messaging_service_sid=self._mid if not is_marketing else self._marketing_mid,
        )

    async def _cancel_scheduled_message(self, message_sid: str) -> Optional[Client.messages]:
        if not message_sid:
            return None
        client = await self._return_authenticated_twilio_client()
        return await client.messages(message_sid).update_async(status="canceled")

    async def _verify_valid_mobile_phone(self, phone_number_str: str) -> bool:
        validated_phone = self.return_e164_phone_formatting(phone_number_str)
        if not validated_phone:
            return False
        url = f"https://lookups.twilio.com/v2/PhoneNumbers/{validated_phone}?Fields=line_type_intelligence"
        acceptable_types = {"mobile", "fixedVoip", "nonFixedVoip", "personal", "tollFree"}
        try:
            async with aiohttp.ClientSession() as session:
                auth = BasicAuth(self._sid, self._key)
                async with session.get(url, auth=auth) as response:
                    if response.status == 200:
                        data = await response.json()
                        line_type = data.get("line_type_intelligence", {}).get("type")
                        return line_type in acceptable_types
                    else:
                        print(f"Error: Received status code {response.status} with body: {await response.text()}")
                        return False
        except Exception as e:
            print(f"Error during Twilio API request: {e}")
            return False

    async def create_event_reminder_text(self, event_data: dict):
        try:
            user = event_data.get("user", {})
            event = event_data.get("event", {})
            to_phone = user.get("phone_number")
            if not to_phone:
                return
            from_phone = self.twilio_marketing_phone
            username = user.get("username", "Cult Member")
            event_name = event.get("name", "Cult Event")
            event_date = event.get("tour_date", "Coming Soon")

            encoded_calendar_event = event.get("encoded_calendar_event", "")
            message_body = (
                f"Hey {username}!\n\n"
                f"The {event_name} is on {event_date}.\n\n"
                "This is another one you will not want to miss."
            )
            if encoded_calendar_event:
                calendar_event_link = f"https://cannabiscult.co/phone/add-calendar-event/{event_data['event_id']}"
                message_body = message_body + f"Add to your calendar: {calendar_event_link}\n\n"
            return message_body, to_phone, from_phone
        except Exception as e:
            print(f"Error creating event reminder text: {e.errors()}")
            return None


def get_twilio_client():
    return TwilioClient()


twilio_client = TwilioClient()
