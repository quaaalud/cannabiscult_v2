#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 30 22:04:15 2023

@author: dale
"""

from typing import Optional, Annotated
from pydantic import BaseModel, EmailStr, Field, confloat, StringConstraints, validator
from schemas.product_types import StrainCategoryEnum


class EdiblesBase(BaseModel):
    cultivator: Annotated[str, StringConstraints(max_length=500)] = Field(..., description="Name of the cultivator")
    strain: Annotated[str, StringConstraints(max_length=500)] = Field(..., description="Name of the strain")
    card_path: Annotated[str, StringConstraints(max_length=500)] = Field(
        ..., description="Path to the edible's image card"
    )
    product_type: str = Field("edible", description="The category for the flower strain. ex: indica, hybrid, etc.")

    @validator("cultivator", "strain", pre=True, always=True)
    def verify_string_and_capitalize_cultivator(cls, v):
        return v.title() if isinstance(v, str) else "Cultivar"

    @validator("strain", pre=True, always=True)
    def verify_string_and_capitalize_strain(cls, v):
        return v.title() if isinstance(v, str) else "CC #"

    class Config:
        from_attributes = True
        strip_whitespace = True
        populate_by_name = True


class Edible(EdiblesBase):
    pass


class MysteryEdibleBase(EdiblesBase):
    pass


class Vibe_Edible_Base(EdiblesBase):
    pass


class Get_Vibe_Edible(Vibe_Edible_Base):
    pass


class EdibleRankingBase(BaseModel):
    strain: Annotated[str, StringConstraints(max_length=500)]
    appearance_rating: confloat = Field(..., gt=0, lt=10.1)
    flavor_rating: confloat = Field(..., gt=0, lt=10.1)
    aftertaste_rating: confloat = Field(..., gt=0, lt=10.1)
    effects_rating: confloat = Field(..., gt=0, lt=10.1)
    appearance_explanation: Optional[Annotated[str, StringConstraints(max_length=500)]] = Field(None, max_length=500)
    flavor_explanation: Optional[Annotated[str, StringConstraints(max_length=500)]] = Field(None, max_length=500)
    aftertaste_explanation: Optional[Annotated[str, StringConstraints(max_length=500)]] = Field(None, max_length=500)
    effects_explanation: Optional[Annotated[str, StringConstraints(max_length=500)]] = Field(None, max_length=500)


class GetEdibleRanking(BaseModel):
    vibe_edible_id: int = Field(...)
    connoisseur: EmailStr = Field(...)
    cultivator: Optional[Annotated[str, StringConstraints(max_length=500)]] = Field(None, max_length=199)
    strain: Annotated[str, StringConstraints(max_length=500)] = Field(..., max_length=200)
    flavor: Annotated[str, StringConstraints(max_length=500)] = Field(..., max_length=200)

    appearance_rating: confloat = Field(..., gt=0, lt=10.1)
    flavor_rating: confloat = Field(..., gt=0, lt=10.1)
    feel_rating: confloat = Field(..., gt=0, lt=10.1)
    chew_rating: confloat = Field(..., gt=0, lt=10.1)
    effects_rating: confloat = Field(..., gt=0, lt=10.1)
    appearance_explanation: Optional[Annotated[str, StringConstraints(max_length=500)]] = Field(None, max_length=500)
    flavor_explanation: Optional[Annotated[str, StringConstraints(max_length=500)]] = Field(None, max_length=500)
    feel_explanation: Optional[Annotated[str, StringConstraints(max_length=500)]] = Field(None, max_length=500)
    chew_explanation: Optional[Annotated[str, StringConstraints(max_length=500)]] = Field(None, max_length=500)
    effects_explanation: Optional[Annotated[str, StringConstraints(max_length=500)]] = Field(None, max_length=500)

    class Config:
        from_attributes = True


class CreateEdibleRanking(BaseModel):
    vibe_edible_id: int = Field(...)
    connoisseur: EmailStr = Field(...)
    cultivator: Optional[Annotated[str, StringConstraints(max_length=500)]] = Field(None, max_length=199)
    strain: Annotated[str, StringConstraints(max_length=500)] = Field(..., max_length=200)
    flavor: Annotated[str, StringConstraints(max_length=500)] = Field(..., max_length=200)

    appearance_rating: confloat = Field(..., gt=0, lt=10.1)
    flavor_rating: confloat = Field(..., gt=0, lt=10.1)
    feel_rating: confloat = Field(..., gt=0, lt=10.1)
    chew_rating: confloat = Field(..., gt=0, lt=10.1)
    effects_rating: confloat = Field(..., gt=0, lt=10.1)
    appearance_explanation: Optional[Annotated[str, StringConstraints(max_length=500)]] = Field(None, max_length=500)
    flavor_explanation: Optional[Annotated[str, StringConstraints(max_length=500)]] = Field(None, max_length=500)
    feel_explanation: Optional[Annotated[str, StringConstraints(max_length=500)]] = Field(None, max_length=500)
    chew_explanation: Optional[Annotated[str, StringConstraints(max_length=500)]] = Field(None, max_length=500)
    effects_explanation: Optional[Annotated[str, StringConstraints(max_length=500)]] = Field(None, max_length=500)

    class Config:
        from_attributes = True


class GetVibeEdibleRanking(GetEdibleRanking):
    pass


class CreateVibeEdibleRanking(CreateEdibleRanking):
    pass
