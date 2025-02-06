#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 11 21:55:38 2023

@author: dale
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional


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
        exclude_unset = True
        populate_by_name = True
        strip_whitespace = True


class ShowMysteryVoter(BaseModel):
    email: EmailStr = Field(..., description="Connoisseur's email address")

    class Config:
        from_attributes = True
        exclude_unset = True
        populate_by_name = True
        strip_whitespace = True
