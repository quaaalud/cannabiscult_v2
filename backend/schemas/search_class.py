#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 22 20:12:30 2023

@author: dale
"""

from pydantic import BaseModel, Field, HttpUrl
from typing import List


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
