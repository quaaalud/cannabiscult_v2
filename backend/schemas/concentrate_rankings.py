#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov  5 16:57:17 2023

@author: dale
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import date
import hashlib


class ConcentrateRankingBase(BaseModel):
    cultivator: str
    strain: str

    color_rating: float = Field(..., gt=0, lt=10.1)
    consistency_rating: float = Field(..., gt=0, lt=10.1)
    smell_rating: float = Field(..., gt=0, lt=10.1)
    flavor_rating: float = Field(..., gt=0, lt=10.1)
    harshness_rating: float = Field(..., gt=0, lt=10.1)
    residuals_rating: float = Field(..., gt=0, lt=10.1)
    effects_rating: float = Field(..., gt=0, lt=10.1)
    color_explanation: Optional[str] = Field(None, max_length=500)
    consistency_explanation: Optional[str] = Field(None, max_length=500)
    flavor_explanation: Optional[str] = Field(None, max_length=500)
    smell_explanation: Optional[str] = Field(None, max_length=500)
    harshness_explanation: Optional[str] = Field(None, max_length=500)
    residuals_explanation: Optional[str] = Field(None, max_length=500)
    effects_explanation: Optional[str] = Field(None, max_length=500)

    class Config:
        from_attributes = True


class CreateConcentrateRanking(ConcentrateRankingBase):
    connoisseur: EmailStr = Field(...)
    concentrate_id: int = Field(...)


class CreateHiddenConcentrateRanking(CreateConcentrateRanking):
    pass


class HiddenConcentrateRanking(BaseModel):
    id: int = Field(..., alias="hidden_concentrate_ranking_id")
    cultivator: Optional[str] = None
    strain: Optional[str] = None
    connoisseur: Optional[str] = None
    color_rating: float
    consistency_rating: float
    smell_rating: float
    flavor_rating: float
    harshness_rating: float
    residuals_rating: float
    effects_rating: float
    date_posted: date

    @validator("connoisseur", pre=True, always=True)
    def obfuscate_email(cls, v):
        return hashlib.sha256(v.encode()).hexdigest()[:6]

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
