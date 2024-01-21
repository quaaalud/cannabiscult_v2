#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan 21 12:53:04 2024

@author: dale
"""

from pydantic import BaseModel, constr, confloat
from datetime import date
from typing import Optional, List


class PreRollSchema(BaseModel):
    cultivator: constr(strict=True)  # Text field
    strain: constr(strict=True)  # Text field
    card_path: Optional[str]  # Text field, nullable
    voting_open: bool = True  # Boolean with default
    pre_roll_id: int  # BigInteger
    is_mystery: bool = True  # Boolean with default

    class Config:
        orm_mode = True


class PreRollDescriptionSchema(BaseModel):
    description_id: int  # BigInteger, autoincrement
    pre_roll_id: Optional[int]  # BigInteger, nullable, foreign key
    description: str = "Coming Soon"  # Text with default
    effects: str = "Coming Soon"  # Text with default
    lineage: str = "Coming Soon"  # Text with default
    terpenes_list: Optional[List[str]]  # Array of Text, nullable
    cultivar_email: str = "aaron.childs@thesocialoutfitus.com"  # Text with default
    unused1: str = "Coming Soon"  # Text with default
    unused2: str = "Coming Soon"  # Text with default

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "description": "A detailed description (less than 1500 characters)",
                "effects": "Effects description (less than 1500 characters)",
                "lineage": "Lineage description (less than 1500 characters)",
            }
        }


class PreRollRankingSchema(BaseModel):
    cultivator: str  # String
    strain: str  # String
    connoisseur: str  # String
    roll_rating: confloat(ge=0)  # Float, non-negative
    smell_rating: confloat(ge=0)  # Float, non-negative
    flavor_rating: confloat(ge=0)  # Float, non-negative
    harshness_rating: confloat(ge=0)  # Float, non-negative
    burn_rating: confloat(ge=0)  # Float, non-negative
    effects_rating: confloat(ge=0)  # Float, non-negative
    roll_explanation: Optional[constr(max_length=500)]  # String(500), nullable
    flavor_explanation: Optional[constr(max_length=500)]  # String(500), nullable
    smell_explanation: Optional[constr(max_length=500)]  # String(500), nullable
    harshness_explanation: Optional[constr(max_length=500)]  # String(500), nullable
    burn_explanation: Optional[constr(max_length=500)]  # String(500), nullable
    effects_explanation: Optional[constr(max_length=500)]  # String(500), nullable
    date_posted: date = None  # Date, default to current date
    pre_roll_id: int  # Integer

    class Config:
        orm_mode = True
