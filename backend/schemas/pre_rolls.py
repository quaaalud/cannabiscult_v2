#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan 21 12:53:04 2024

@author: dale
"""

from pydantic import BaseModel, Field, constr, confloat
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
    pre_roll_ranking_id: int = Field(
        ..., description="The unique identifier for the pre-roll ranking"
    )
    cultivator: str = Field(..., description="Name of the cultivator")
    strain: str = Field(..., description="Name of the strain")
    connoisseur: str = Field(..., description="Name of the connoisseur")
    roll_rating: confloat(ge=0) = Field(..., description="Rating for the roll quality")
    airflow_rating: confloat(ge=0) = Field(..., description="Rating for airflow quality")
    ease_to_light_rating: confloat(ge=0) = Field(
        ..., description="Rating for ease of lighting pre-roll"
    )
    flavor_rating: confloat(ge=0) = Field(..., description="Rating for the flavor")
    tightness_rating: confloat(ge=0) = Field(..., description="Rating for tightness of the roll")
    burn_rating: confloat(ge=0) = Field(..., description="Rating for the burn quality")
    effects_rating: confloat(ge=0) = Field(..., description="Rating for the effects")
    overall_score: confloat(ge=0) = Field(
        ..., description="Overall score calculated from the ratings"
    )
    roll_explanation: Optional[constr(max_length=500)] = Field(
        None, description="Explanation for the roll rating"
    )
    ease_to_light_explanation: Optional[constr(max_length=500)] = Field(
        None, description="Explanation for ease of lighting pre-roll rating"
    )
    flavor_explanation: Optional[constr(max_length=500)] = Field(
        None, description="Explanation for the flavor rating"
    )
    airflow_explanation: Optional[constr(max_length=500)] = Field(
        None, description="Explanation for the airflow rating"
    )
    tightness_explanation: Optional[constr(max_length=500)] = Field(
        None, description="Explanation for the tightness of the roll rating"
    )
    burn_explanation: Optional[constr(max_length=500)] = Field(
        None, description="Explanation for the burn rating"
    )
    effects_explanation: Optional[constr(max_length=500)] = Field(
        None, description="Explanation for the effects rating"
    )
    purchase_bool: bool = Field(
        ..., description="Indicates whether the pre-roll would be purchased again"
    )
    batch_id: Optional[str] = Field(
        "Not Provided", description="Batch ID of the pre-roll, if provided"
    )
    date_posted: Optional[date] = Field(None, description="Date when the ranking was posted")
    pre_roll_id: int = Field(..., description="ID of the associated pre-roll")

    class Config:
        orm_mode = True
