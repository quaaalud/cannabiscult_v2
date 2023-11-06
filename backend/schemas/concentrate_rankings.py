#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov  5 16:57:17 2023

@author: dale
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class ConcentrateRankingBase(BaseModel):
    cultivator: str
    strain: str
    
    color_rating: float = Field(..., gt=0, lt=10.1)
    consitency_rating: float = Field(..., gt=0, lt=10.1)
    smell_rating: float = Field(..., gt=0, lt=10.1)
    flavor_rating: float = Field(..., gt=0, lt=10.1)
    harshness_rating: float = Field(..., gt=0, lt=10.1)
    effects_rating: float = Field(..., gt=0, lt=10.1)
    color_explanation: Optional[str] = Field(None, max_length=500)
    consitency_explanation: float = Field(..., gt=0, lt=10.1)
    flavor_explanation: Optional[str] = Field(None, max_length=500)
    smell_explanation: Optional[str] = Field(None, max_length=500)
    harshness_explanation: Optional[str] = Field(None, max_length=500)
    effects_explanation: Optional[str] = Field(None, max_length=500)
    
    class Config():
        from_attributes = True


class CreateConcentrateRanking(ConcentrateRankingBase):
    voter_email: EmailStr = Field(...)


class CreateHiddenConcentrateRanking(CreateConcentrateRanking):
    concentrate_id: int = Field(...)
    hidden_concentrate_ranking_id: int = Field(...)