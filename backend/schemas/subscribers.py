#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr 15 20:04:19 2023

@author: dale
"""

from pydantic import BaseModel, EmailStr, Field, field_validator


class SubscriberCreate(BaseModel):
    email: EmailStr = Field(..., description="Subscriber's email address")
    name: str = Field(..., description="Subscriber's full name")
    zip_code: str = Field(..., description="Subscriber's postal zip code")
    phone: str = Field(
        ..., description="Subscriber's phone number", min_length=10,
    )

    @field_validator("phone", mode="before")
    def validate_and_format_phone_number(cls, v):
        v = "".join(filter(str.isdigit, v))
        if v.startswith("1") and (len(v) == 11):
            v = f"{v[1:]}"
        return f"{v[0:11]}"

    class Config:
        from_attributes = True
        populate_by_name = True
        strip_whitespace = True
        exclude_unset = True


class ShowSubscriber(BaseModel):
    email: EmailStr = Field(..., description="Subscriber's email address")

    class Config:
        from_attributes = True
        strip_whitespace = True
        populate_by_name = True
        exclude_unset = True
