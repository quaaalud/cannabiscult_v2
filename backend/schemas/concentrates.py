#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov  5 16:47:38 2023

@author: dale
"""

from typing import Annotated
from pydantic import BaseModel, Field, StringConstraints, validator, root_validator


class ConcentratesBase(BaseModel):
    concentrate_id: int = Field(..., description="Unique identifier for the concentrate")
    cultivator: Annotated[str, StringConstraints(max_length=500)] = Field(..., description="Name of the cultivator")
    strain: Annotated[str, StringConstraints(max_length=500)] = Field(..., description="Name of the strain")
    is_mystery: bool = Field(..., description="Indicates if the concentrate is a mystery product")
    card_path: Annotated[str, StringConstraints(max_length=500)] = Field(
        ..., description="Path to the concentrate's image card"
    )
    voting_open: bool = Field(True, description="Indicates if voting is open for this concentrate")

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


class HiddenConcentrate(ConcentratesBase):
    pass

    @root_validator(pre=True)
    def mask_cultivator(cls, values):
        if values.get("is_mystery", False):
            values["cultivator"] = "Cultivar"
        return values
