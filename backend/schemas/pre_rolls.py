#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan 21 12:53:04 2024

@author: dale
"""

from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional, List, Annotated

OptionalStr = Annotated[Optional[str], Field(None, max_length=500)]


class PreRollSchema(BaseModel):
    cultivator: OptionalStr(strict=True) = Field(..., description="Name of the cultivator")
    strain: OptionalStr(strict=True) = Field(..., description="Name of the strain")
    card_path: Optional[str] = Field(None, description="Path to the pre-roll's image card")
    voting_open: bool = Field(True, description="Flag to indicate if voting is open")
    pre_roll_id: int = Field(..., description="Unique identifier for the pre-roll")
    is_mystery: bool = Field(True, description="Flag to indicate if the pre-roll is a mystery roll")
    product_type: str = Field("pre-roll", description="Product Type for Pre-Rolls")

    @validator("cultivator", "strain", pre=True, always=True)
    def verify_string_and_capitalize_name(cls, v):
        return v.title() if isinstance(v, str) else "None Submitted"

    class Config:
        from_attributes = True
        exclude_unset = True
        populate_by_name = True
        strip_whitespace = True


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
    cultivator: str = Field(..., description="Name of the cultivator")
    strain: str = Field(..., description="Name of the strain")
    connoisseur: EmailStr = Field(..., description="Email address of the connoisseur")
    roll_rating: float = Field(None, gt=0, lt=10.1, description="Rating for the roll quality")
    airflow_rating: Optional[float] = Field(
        None, gt=0, lt=10.1, description="Rating for airflow quality"
    )
    ease_to_light_rating: Optional[float] = Field(
        None, gt=0, lt=10.1, description="Rating for ease of lighting pre-roll"
    )
    flavor_rating: Optional[float] = Field(None, gt=0, lt=10.1, description="Rating for the flavor")
    tightness_rating: Optional[float] = Field(
        None, gt=0, lt=10.1, description="Rating for tightness of the roll"
    )
    burn_rating: Optional[float] = Field(
        None, gt=0, lt=10.1, description="Rating for the burn quality"
    )
    effects_rating: Optional[float] = Field(
        None, gt=0, lt=10.1, description="Rating for the effects"
    )
    overall_score: Optional[float] = Field(
        None, gt=0, lt=10.1, description="Overall score calculated from the ratings"
    )

    roll_explanation: Optional[str] = Field(
        None, max_length=500, description="Explanation for the roll rating"
    )
    airflow_explanation: Optional[str] = Field(
        None, max_length=500, description="Explanation for the airflow rating"
    )
    ease_to_light_explanation: Optional[str] = Field(
        None, max_length=500, description="Explanation for ease of lighting pre-roll rating"
    )
    flavor_explanation: Optional[str] = Field(
        None, max_length=500, description="Explanation for the flavor rating"
    )
    tightness_explanation: Optional[str] = Field(
        None, max_length=500, description="Explanation for the tightness of the roll rating"
    )
    burn_explanation: Optional[str] = Field(
        None, max_length=500, description="Explanation for the burn rating"
    )
    effects_explanation: Optional[str] = Field(
        None, max_length=500, description="Explanation for the effects rating"
    )
    purchase_bool: Optional[bool] = Field(True, description="Would you buy product again?")
    pack_code: Optional[str] = Field(
        None, max_length=99, description="Pack code of the pre-roll, if provided"
    )
    pre_roll_id: int = Field(..., description="ID of the associated pre-roll")

    @validator("cultivator", "strain", pre=True, always=True)
    def verify_string_and_capitalize_name(cls, v):
        return v.title() if isinstance(v, str) else "None Submitted"

    class Config:
        from_attributes = True
        exclude_unset = True
        populate_by_name = True
        strip_whitespace = True
