#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov  5 16:57:17 2023

@author: dale
"""

from pydantic import BaseModel, EmailStr, Field, constr, confloat
from typing import Optional
from datetime import date


class ConcentrateRankingBase(BaseModel):
    cultivator: constr(strict=True) = Field(..., description="Name of the cultivator")
    strain: constr(strict=True) = Field(..., description="Name of the strain")
    color_rating: confloat(gt=0, lt=10.1) = Field(..., description="Color rating, range 0-10")
    consistency_rating: confloat(gt=0, lt=10.1) = Field(
        ..., description="Consistency rating, range 0-10"
    )
    smell_rating: confloat(gt=0, lt=10.1) = Field(..., description="Smell rating, range 0-10")
    flavor_rating: confloat(gt=0, lt=10.1) = Field(..., description="Flavor rating, range 0-10")
    harshness_rating: confloat(gt=0, lt=10.1) = Field(
        ..., description="Harshness rating, range 0-10"
    )
    residuals_rating: confloat(gt=0, lt=10.1) = Field(
        ..., description="Residuals rating, range 0-10"
    )
    effects_rating: confloat(gt=0, lt=10.1) = Field(..., description="Effects rating, range 0-10")
    color_explanation: Optional[str] = Field(
        None, max_length=500, description="Explanation for the color rating"
    )
    consistency_explanation: Optional[str] = Field(
        None, max_length=500, description="Explanation for the consistency rating"
    )
    flavor_explanation: Optional[str] = Field(
        None, max_length=500, description="Explanation for the flavor rating"
    )
    smell_explanation: Optional[str] = Field(
        None, max_length=500, description="Explanation for the smell rating"
    )
    harshness_explanation: Optional[str] = Field(
        None, max_length=500, description="Explanation for the harshness rating"
    )
    residuals_explanation: Optional[str] = Field(
        None, max_length=500, description="Explanation for the residuals rating"
    )
    effects_explanation: Optional[str] = Field(
        None, max_length=500, description="Explanation for the effects rating"
    )
    pack_code: Optional[str] = Field(
        None, max_length=99, description="Pack code of the concentrate, if provided"
    )

    class Config:
        from_attributes = True
        populate_by_name = True


class CreateConcentrateRanking(ConcentrateRankingBase):
    connoisseur: EmailStr = Field(..., description="Email of the connoisseur")
    concentrate_id: int = Field(..., description="Unique identifier for the concentrate")


class CreateHiddenConcentrateRanking(CreateConcentrateRanking):
    pass


class HiddenConcentrateRanking(CreateHiddenConcentrateRanking):
    pass
