#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr 15 20:04:19 2023

@author: dale
"""

from pydantic import BaseModel, EmailStr, Field


class SubscriberCreate(BaseModel):
    email: EmailStr = Field(..., description="Subscriber's email address")
    name: str = Field(..., description="Subscriber's full name")
    zip_code: str = Field(..., description="Subscriber's postal zip code")
    phone: str = Field(
        ..., description="Subscriber's phone number", min_length=10, pattern="^[0-9]+$"
    )


class ShowSubscriber(BaseModel):
    email: EmailStr = Field(..., description="Subscriber's email address")

    class Config:
        from_attributes = True
