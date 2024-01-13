#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 11 21:55:38 2023

@author: dale
"""

from pydantic import BaseModel, EmailStr, validator
from typing import Optional


class MysteryVoterCreate(BaseModel):
    email: EmailStr
    name: str
    zip_code: str
    phone: str
    industry_employer: Optional[str] = None
    industry_job_title: Optional[str] = None


class ShowMysteryVoter(BaseModel):
    email: EmailStr

    class Config:
        from_attributes = True


class StrainGuessInput(BaseModel):
    strain_guesses: dict
    email: EmailStr

    @validator("strain_guesses")
    def validate_strain_guesses(cls, v):
        if not isinstance(v, dict):
            raise ValueError("strain_guesses must be a dictionary")
        if not all(isinstance(key, str) and isinstance(value, str) for key, value in v.items()):
            raise ValueError(
                "strain_guesses must be a dictionary with string keys and integer values"
            )
        return v

    class Config:
        from_attributes = True
        schema_extra = {
            "example": {
                "strain_guesses": {"Citrus 1": "strain_guess", "Citrus 2": "strain_guess"},
                "email": "example@example.com",
            }
        }
