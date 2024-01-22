#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov  5 16:47:38 2023

@author: dale
"""

from pydantic import BaseModel, constr, EmailStr, root_validator, Field
from typing import List, Optional


class FlowersBase(BaseModel):
    flower_id: int = Field(..., description="Unique identifier for the flower")
    cultivator: str = Field(..., description="Name of the cultivator")
    strain: str = Field(..., description="Name of the strain")
    is_mystery: bool = Field(..., description="Indicates if the flower is a mystery")
    card_path: str = Field(..., description="Path to the flower's image card")
    voting_open: bool = Field(True, description="Indicates if voting is open for this flower")
    product_type: str = Field("flower", description="Type of the product, default is 'flower'")

    class Config:
        from_attributes = True


class HiddenFlower(FlowersBase):
    @root_validator(pre=True)
    def mask_cultivator(cls, values):
        if values.get("is_mystery", False):
            values["cultivator"] = "Hidden"
        return values


class FlowerDescriptionBase(BaseModel):
    flower_id: int = Field(..., description="Unique identifier for the flower")
    description: constr(max_length=1500) = Field(
        "Coming Soon", description="Description of the flower, max 1500 characters"
    )
    effects: constr(max_length=1500) = Field(
        "Coming Soon", description="Effects of the flower, max 1500 characters"
    )
    lineage: constr(max_length=1500) = Field(
        "Coming Soon", description="Lineage of the flower, max 1500 characters"
    )
    terpenes_list: Optional[List[str]] = Field(None, description="List of terpenes in the flower")
    cultivar_email: EmailStr = Field(..., description="Email of the cultivar")

    class Config:
        from_attributes = True


class AddFlowerDescription(FlowerDescriptionBase):
    pass


class GetFlowerDescription(FlowerDescriptionBase):
    description_id: int = Field(..., description="Unique identifier for the flower description")
