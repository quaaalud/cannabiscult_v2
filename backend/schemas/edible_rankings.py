#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 30 19:40:53 2023

@author: dale
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class EdibleRankingBase(BaseModel):
    strain: str
    appearance_rating: float = Field(..., gt=0, lt=10.1)
    flavor_rating: float = Field(..., gt=0, lt=10.1)
    aftertaste_rating: float = Field(..., gt=0, lt=10.1)
    effects_rating: float = Field(..., gt=0, lt=10.1)
    appearance_explanation: Optional[str] = Field(None, max_length=500)
    flavor_explanation: Optional[str] = Field(None, max_length=500)
    aftertaste_explanation: Optional[str] = Field(None, max_length=500)
    effects_explanation: Optional[str] = Field(None, max_length=500)


class CreateMysteryEdibleRanking(EdibleRankingBase):
    voter_email: EmailStr = Field(...)
    
    class Config():
        from_attributes = True
        

class CreateVividEdibleRanking(EdibleRankingBase):
    vivid_edible_id: int = Field(...)
    connoisseur: EmailStr = Field(...)
    cultivator: Optional[str] = Field(None, max_length=199)
    
    class Config():
        from_attributes = True


class CreateVibeEdibleRanking(BaseModel):
    vibe_edible_id: int = Field(...)
    connoisseur: EmailStr = Field(...)
    cultivator: Optional[str] = Field(None, max_length=199)
    strain: str = Field(..., max_length=200)
    flavor: str = Field(..., max_length=200)
    
    appearance_rating: float = Field(..., gt=0, lt=10.1)
    flavor_rating: float = Field(..., gt=0, lt=10.1)
    feel_rating: float = Field(..., gt=0, lt=10.1)
    chew_rating: float = Field(..., gt=0, lt=10.1)
    effects_rating: float = Field(..., gt=0, lt=10.1)
    appearance_explanation: Optional[str] = Field(None, max_length=500)
    flavor_explanation: Optional[str] = Field(None, max_length=500)
    feel_explanation: Optional[str] = Field(None, max_length=500)
    chew_explanation: Optional[str] = Field(None, max_length=500)
    effects_explanation: Optional[str] = Field(None, max_length=500)
    
    class Config():
        from_attributes = True