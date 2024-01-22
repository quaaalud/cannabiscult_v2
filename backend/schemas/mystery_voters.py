#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 11 21:55:38 2023

@author: dale
"""

from pydantic import BaseModel, EmailStr, validator, Field
from typing import Optional, Dict


class MysteryVoterCreate(BaseModel):
    email: EmailStr = Field(..., description="Connoisseur's email address")
    name: str = Field(..., description="Connoisseur's full name")
    zip_code: str = Field(..., description="Connoisseur's zip code")
    phone: str = Field(..., description="Connoisseur's phone number")
    industry_employer: Optional[str] = Field(
        None, description="Connoisseur's employer in the industry, if any"
    )
    industry_job_title: Optional[str] = Field(
        None, description="Connoisseur's job title in the industry, if any"
    )

    class Config:
        from_attributes = True


class ShowMysteryVoter(BaseModel):
    email: EmailStr = Field(..., description="Connoisseur's email address")

    class Config:
        from_attributes = True


class StrainGuessInput(BaseModel):
    strain_guesses: Dict = Field(..., description="Dictionary of strain guesses")
    email: EmailStr = Field(..., description="Connoisseur's email address")

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
        json_schema_extra = {
            "example": {
                "strain_guesses": {"Citrus 1": "strain_guess", "Citrus 2": "strain_guess"},
                "email": "example@example.com",
            }
        }
