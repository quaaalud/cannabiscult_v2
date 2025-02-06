#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 30 19:40:53 2023

@author: dale
"""

from typing import Optional, Annotated
from pydantic import BaseModel, EmailStr, Field, confloat, StringConstraints


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


class CreateMysteryEdibleRanking(EdibleRankingBase):
    voter_email: EmailStr = Field(...)

    class Config:
        from_attributes = True


class CreateVividEdibleRanking(EdibleRankingBase):
    vivid_edible_id: int = Field(...)
    connoisseur: EmailStr = Field(...)
    cultivator: Optional[Annotated[str, StringConstraints(max_length=500)]] = Field(None, max_length=199)

    class Config:
        from_attributes = True


class GetVibeEdibleRanking(BaseModel):
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


class CreateVibeEdibleRanking(BaseModel):
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
