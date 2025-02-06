#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 30 22:04:15 2023

@author: dale
"""

from typing import Annotated
from pydantic import BaseModel, Field, StringConstraints, validator


class EdiblesBase(BaseModel):
    cultivator: Annotated[str, StringConstraints(max_length=500)] = Field(..., description="Name of the cultivator")
    strain: Annotated[str, StringConstraints(max_length=500)] = Field(..., description="Name of the strain")
    card_path: Annotated[str, StringConstraints(max_length=500)] = Field(
        ..., description="Path to the edible's image card"
    )
    product_type: str = Field(
         "edible", description="The category for the flower strain. ex: indica, hybrid, etc."
    )

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
