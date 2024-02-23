#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov  5 16:57:17 2023

@author: dale
"""

from pydantic import BaseModel, EmailStr, Field, constr, confloat
from typing import Optional


class FlowerRankingBase(BaseModel):
    strain: str

    appearance_rating: float = Field(..., gt=0, lt=10.1)
    freshness_rating: float = Field(..., gt=0, lt=10.1)
    smell_rating: float = Field(..., gt=0, lt=10.1)
    flavor_rating: float = Field(..., gt=0, lt=10.1)
    harshness_rating: float = Field(..., gt=0, lt=10.1)
    effects_rating: float = Field(..., gt=0, lt=10.1)
    appearance_explanation: Optional[str] = Field(None, max_length=500)
    freshness_explanation: Optional[str] = Field(None, max_length=500)
    flavor_explanation: Optional[str] = Field(None, max_length=500)
    smell_explanation: Optional[str] = Field(None, max_length=500)
    harshness_explanation: Optional[str] = Field(None, max_length=500)
    effects_explanation: Optional[str] = Field(None, max_length=500)

    pack_code: Optional[str] = Field(None, max_length=99)
    flower_id: int = Field(...)

    class Config:
        from_attributes = True


class FlowerVoteCreate(BaseModel):
    cultivator_selected: str = Field(..., description="Selected cultivator's name")
    strain_selected: str = Field(..., description="Selected strain's name")
    structure_vote: constr(max_length=50) = Field(
        ..., description="Vote for the structure of the flower"
    )
    structure_explanation: constr(max_length=500) = Field(
        ..., description="Explanation for the structure vote"
    )
    nose_vote: confloat(ge=0, le=10) = Field(
        ..., description="Vote for the nose/fragrance of the flower, from 0 to 10"
    )
    nose_explanation: constr(max_length=500) = Field(
        ..., description="Explanation for the nose vote"
    )
    flavor_vote: confloat(ge=0, le=10) = Field(
        ..., description="Vote for the flavor of the flower, from 0 to 10"
    )
    flavor_explanation: constr(max_length=500) = Field(
        ..., description="Explanation for the flavor vote"
    )
    effects_vote: confloat(ge=0, le=10) = Field(
        ..., description="Vote for the effects of the flower, from 0 to 10"
    )
    effects_explanation: constr(max_length=500) = Field(
        ..., description="Explanation for the effects vote"
    )
    user_email: EmailStr = Field(..., description="Email address of the connoisseur")

    class Config:
        from_attributes = True


class CreateFlowerRanking(FlowerRankingBase):
    cultivator: str
    method_of_consumption: str = Field(
        ..., description="Method of Connsumption for the reviewed strain."
    )
    connoisseur: EmailStr = Field(..., description="Email address of the connoisseur")


class CreateHiddenFlowerRanking(CreateFlowerRanking):
    pass


class GetFlowerRanking(CreateFlowerRanking):
    class Config:
        from_attributes = True
        populate_by_name = True
