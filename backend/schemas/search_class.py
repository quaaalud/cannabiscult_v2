#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 22 20:12:30 2023

@author: dale
"""

from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional


class SearchResultItem(BaseModel):
    cultivator: str = Field(..., description="Name of the cultivator")
    strain: str = Field(..., description="Name of the strain")
    type: str = Field(..., description="Type of the product")
    url_path: HttpUrl = Field(..., description="URL path to the product details")

    class Config:
        from_attributes = True


class SearchResults(BaseModel):
    results: List[SearchResultItem] = Field(..., description="List of search result items")


class StrainCultivator(BaseModel):
    strain: str
    cultivator: str


class RatingModel(BaseModel):
    product_type: str
    strain: str
    cultivator: str
    appearance_rating: Optional[float] = Field(..., gt=-1, lt=11)
    smell_rating: Optional[float] = Field(..., gt=-1, lt=11)
    freshness_rating: Optional[float] = Field(..., gt=-1, lt=11)
    flavor_rating: Optional[float] = Field(..., gt=-1, lt=11)
    harshness_rating: Optional[float] = Field(..., gt=-1, lt=11)
    effects_rating: Optional[float] = Field(..., gt=-1, lt=11)
    cult_rating: Optional[float] = Field(..., gt=-1, lt=11)

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "product_type": "Flower",
                "strain": "Missouri Belle",
                "cultivator": "Mo Dank",
                "appearance_rating": 7.67,
                "smell_rating": 8.67,
                "freshness_rating": 8.33,
                "flavor_rating": 8.67,
                "harshness_rating": 8.33,
                "effects_rating": 8,
                "cult_rating": 8.28
            }
        }
