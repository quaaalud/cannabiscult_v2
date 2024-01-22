#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul  3 15:44:00 2023

@author: dale
"""

from pydantic import BaseModel, Field, constr, confloat
from typing import List


class FlowerReviewCreate(BaseModel):
    cultivator: str = Field(..., description="Name of the cultivator")
    strain: str = Field(..., description="Name of the strain")
    overall: confloat(ge=0, le=10) = Field(
        ..., description="Overall rating for the flower, from 0 to 10"
    )
    structure: confloat(ge=0, le=10) = Field(
        ..., description="Rating for the structure of the flower, from 0 to 10"
    )
    nose: confloat(ge=0, le=10) = Field(
        ..., description="Rating for the nose/fragrance of the flower, from 0 to 10"
    )
    flavor: confloat(ge=0, le=10) = Field(
        ..., description="Rating for the flavor of the flower, from 0 to 10"
    )
    effects: confloat(ge=0, le=10) = Field(
        ..., description="Rating for the effects of the flower, from 0 to 10"
    )
    card_path: constr = Field(..., description="Path to the flower's image card")

    class Config:
        from_attributes = True


class FlowerReviewUpdate(BaseModel):
    review_id: int = Field(..., description="Unique identifier for the review")
    structure: confloat(ge=0, le=10) = Field(
        ..., description="Updated rating for the structure of the flower, from 0 to 10"
    )
    nose: confloat(ge=0, le=10) = Field(
        ..., description="Updated rating for the nose/fragrance of the flower, from 0 to 10"
    )
    flavor: confloat(ge=0, le=10) = Field(
        ..., description="Updated rating for the flavor of the flower, from 0 to 10"
    )
    effects: confloat(ge=0, le=10) = Field(
        ..., description="Updated rating for the effects of the flower, from 0 to 10"
    )

    class Config:
        from_attributes = True


class ShowFlowerReview(BaseModel):
    cultivator: constr = Field(..., description="Name of the cultivator")
    strain: constr = Field(..., description="Name of the strain")
    overall: confloat(ge=0, le=10) = Field(
        ..., description="Overall rating for the flower, from 0 to 10"
    )
    structure: confloat(ge=0, le=10) = Field(
        ..., description="Rating for the structure of the flower, from 0 to 10"
    )
    nose: confloat(ge=0, le=10) = Field(
        ..., description="Rating for the nose/fragrance of the flower, from 0 to 10"
    )
    flavor: confloat(ge=0, le=10) = Field(
        ..., description="Rating for the flavor of the flower, from 0 to 10"
    )
    effects: confloat(ge=0, le=10) = Field(
        ..., description="Rating for the effects of the flower, from 0 to 10"
    )
    vote_count: int = Field(..., description="Number of votes received")
    card_path: constr = Field(..., description="Path to the flower's image card")
    terpene_list: List[constr] = Field(..., description="List of terpenes found in the flower")

    class Config:
        from_attributes = True
