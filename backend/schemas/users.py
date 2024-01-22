#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 10 20:51:36 2023

@author: dale
"""

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    username: str = Field(..., description="User's unique username")
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., description="User's password")
    name: str = Field(..., description="User's full name")
    zip_code: str = Field(..., description="User's postal zip code")
    phone: str = Field(..., description="User's phone number")
    agree_tos: bool = Field(False, description="Agreement to terms of service")
    can_vote: bool = Field(False, description="Eligibility to vote")
    is_superuser: bool = Field(False, description="Admin status")


class UserLogin(BaseModel):
    email: EmailStr = Field(..., description="User's email address for login")
    password: str = Field(..., description="User's password for login")


class ShowUser(BaseModel):
    username: str = Field(..., description="User's username")
    can_vote: bool = Field(..., description="Indicates if the user can vote")

    class Config:
        from_attributes = True


class LoggedInUser(BaseModel):
    username: str = Field(..., description="User's username")
    email: EmailStr = Field(..., description="User's email address")
    can_vote: bool = Field(..., description="Indicates if the user can vote")
    role: str = Field(..., description="User's role in the system")

    class Config:
        from_attributes = True
