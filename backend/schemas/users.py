#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 10 20:51:36 2023

@author: dale
"""

from uuid import UUID
from typing import Optional, Union
from pydantic import BaseModel, EmailStr, Field, validator


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
    auth_id: Optional[str] = Field(None, description="Optional auth_id value for the user.")

    class Config:
        from_attributes = True
        strip_whitespace = True
        populate_by_name = True
        exclude_unset = True


class UserLogin(BaseModel):
    email: EmailStr = Field(..., description="User's email address for login")
    password: str = Field(..., description="User's password for login")

    class Config:
        from_attributes = True
        strip_whitespace = True
        populate_by_name = True
        exclude_unset = True


class ShowUser(BaseModel):
    username: str = Field(..., description="User's username.")
    can_vote: bool = Field(..., description="Indicates if the user can vote.")
    is_superuser: bool = Field(False, description="Indicates superuser status.")
    auth_id: Optional[str] = Field("", description="Optional auth_id value for the user.")

    @validator("auth_id", pre=True)
    def convert_uuid_to_str_if_needed(cls, v):
        return str(v)

    class Config:
        from_attributes = True
        strip_whitespace = True
        populate_by_name = True
        exclude_unset = True


class LoggedInUser(BaseModel):
    username: str = Field(..., description="User's username")
    email: EmailStr = Field(..., description="User's email address")
    can_vote: bool = Field(..., description="Indicates if the user can vote")
    role: str = Field(..., description="User's role in the system")

    class Config:
        from_attributes = True
        strip_whitespace = True
        populate_by_name = True
        exclude_unset = True


class UserIdSchema(BaseModel):
    user_id: Union[UUID, str] = Field(..., description="User's email address for validations")

    @validator("user_id", pre=True)
    def check_not_empty(cls, v):
        if isinstance(v, UUID):
            v
        return UUID(v)

    class Config:
        from_attributes = True
        strip_whitespace = True
        populate_by_name = True
        exclude_unset = True


class EncodedUserEmailSchema(BaseModel):
    email: str = Field(..., description="User's email address for validations")

    class Config:
        from_attributes = True
        strip_whitespace = True
        populate_by_name = True
        exclude_unset = True


class UserEmailSchema(BaseModel):
    email: EmailStr = Field(..., description="User's email address for login")

    class Config:
        from_attributes = True
        strip_whitespace = True
        populate_by_name = True
        exclude_unset = True


class UserStrainListSubmit(BaseModel):
    strain: str = Field(..., description="Name of the cannabis strain")
    cultivator: str = Field(..., description="Name of the cultivator of the strain")
    to_review: bool = Field(
        default=True, description="Flag indicating if the strain needs to be reviewed"
    )
    product_type: str = Field(..., description="Product type for the strain notes")
    strain_notes: str = Field("N/A", description="User's strain notes")

    @validator("product_type", "strain", "cultivator", "to_review", pre=True)
    def check_not_empty(cls, v):
        if v == "":
            raise ValueError("Field must not be empty")
        return v

    class Config:
        from_attributes = True
        strip_whitespace = True
        populate_by_name = True
        exclude_unset = True


class UserStrainListRemove(BaseModel):
    email: EmailStr = Field(
        ..., description="User's email address linked to the strain list"
    )
    strain: str = Field(..., description="Name of the cannabis strain")
    cultivator: str = Field(..., description="Name of the cultivator of the strain")
    product_type: str = Field(..., description="Product type for the strain notes")

    @validator("*", pre=True)
    def check_not_empty(cls, v):
        if v == "":
            raise ValueError("Field must not be empty")
        return v

    class Config:
        from_attributes = True
        strip_whitespace = True
        populate_by_name = True
        exclude_unset = True


class UserStrainListCreate(BaseModel):
    email: EmailStr = Field(
        ..., description="User's email address linked to the strain list"
    )
    strain: str = Field(..., description="Name of the cannabis strain")
    cultivator: str = Field(..., description="Name of the cultivator of the strain")
    to_review: bool = Field(
        default=True, description="Flag indicating if the strain needs to be reviewed"
    )
    product_type: str = Field(..., description="Product type for the strain notes")
    strain_notes: str = Field("N/A", description="User's strain notes")

    @validator("*", pre=True)
    def check_not_empty(cls, v):
        if v == "":
            raise ValueError("Field must not be empty")
        return v

    class Config:
        from_attributes = True
        strip_whitespace = True
        populate_by_name = True
        exclude_unset = True


class UserStrainListUpdate(BaseModel):
    to_review: bool = Field(
        None, description="Flag indicating if the strain needs to be reviewed"
    )

    @validator("*", pre=True)
    def check_not_empty(cls, v):
        if v == "":
            raise ValueError("Field must not be empty")
        return v

    class Config:
        from_attributes = True
        strip_whitespace = True
        populate_by_name = True
        exclude_unset = True


class UserStrainListSchema(BaseModel):
    id: int = Field(..., description="Unique identifier for the strain list entry")
    email: EmailStr = Field(
        ..., description="User's email address linked to the strain list"
    )
    strain: str = Field(..., description="Name of the cannabis strain")
    cultivator: str = Field(..., description="Name of the cultivator of the strain")
    to_review: bool = Field(
        ..., description="Flag indicating if the strain needs to be reviewed"
    )
    product_type: str = Field(..., description="Product type for the strain notes")
    strain_notes: str = Field("N/A", description="User's strain notes")

    @validator("product_type", pre=True)
    def convert_product_type_to_lower(cls, v):
        return str(v).lower()

    class Config:
        from_attributes = True
        populate_by_name = True
        exclude_unset = True
        strip_whitespace = True


class AddUserStrainListNotes(BaseModel):
    email: EmailStr = Field(
        ..., description="User's email address linked to the strain list"
    )
    strain: str = Field(..., description="Name of the cannabis strain")
    cultivator: str = Field(..., description="Name of the cultivator of the strain")
    to_review: bool = Field(
        ..., description="Flag indicating if the strain needs to be reviewed"
    )
    product_type: str = Field(..., description="Product type for the strain notes")
    strain_notes: str = Field("N/A", description="User's strain notes")

    class Config:
        from_attributes = True
        exclude_unset = True
        populate_by_name = True
        strip_whitespace = True


class MoluvHeadstashFavoriteVoteSchema(BaseModel):
    user_id: Union[UUID, str] = Field(..., description="User ID from the auth.users table.")
    product_type: str = Field(..., description="Product type for the Mo Luv favorite strain vote.")
    product_id: int = Field(..., description="Unique identifier for the strain list entry")

    @validator("user_id", pre=True)
    def check_not_empty(cls, v):
        if isinstance(v, UUID):
            v
        return UUID(v)

    class Config:
        from_attributes = True
        strip_whitespace = True
        populate_by_name = True
        exclude_unset = True


class MoluvHeadstashFavoriteVoteResult(BaseModel):
    product_type: str = Field(..., description="Product type for the Mo Luv favorite strain vote.")
    product_id: int = Field(..., description="Unique identifier for the strain list entry")

    class Config:
        from_attributes = True
        strip_whitespace = True
        populate_by_name = True
        exclude_unset = True
