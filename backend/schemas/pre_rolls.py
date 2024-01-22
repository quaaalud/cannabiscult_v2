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
    cultivator: constr(strict=True) = Field(..., description="Name of the cultivator")
    strain: constr(strict=True) = Field(..., description="Name of the strain")
    card_path: Optional[str] = Field(None, description="Path to the pre-roll's image card")
    voting_open: bool = Field(True, description="Flag to indicate if voting is open")
    pre_roll_id: int = Field(..., description="Unique identifier for the pre-roll")
    is_mystery: bool = Field(True, description="Flag to indicate if the pre-roll is a mystery roll")
    product_type: str = Field('pre-roll', description="Product Type for Pre-Rolls")

    class Config:
        from_attributes = True


class PreRollDescriptionSchema(BaseModel):
    description_id: int = Field(..., description="Unique identifier for the pre-roll description")
    pre_roll_id: Optional[int] = Field(None, description="Associated pre-roll ID")
    description: str = Field("Coming Soon", description="Description of the pre-roll")
    effects: str = Field("Coming Soon", description="Effects of the pre-roll")
    lineage: str = Field("Coming Soon", description="Lineage of the pre-roll")
    terpenes_list: Optional[List[str]] = Field(None, description="List of terpenes in the pre-roll")
    cultivar_email: str = Field(
        "aaron.childs@thesocialoutfitus.com", description="Email of the Connoisseur"
    )
    unused1: str = Field("Coming Soon", description="Placeholder field")
    unused2: str = Field("Coming Soon", description="Another placeholder field")

    class Config:
        from_attributes = True
        json_schema_extra = {
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
        from_attributes = True
