#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 11 21:55:38 2023

@author: dale
"""

from pydantic import BaseModel, EmailStr
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
