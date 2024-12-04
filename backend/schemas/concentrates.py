#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov  5 16:47:38 2023

@author: dale
"""

from pydantic import BaseModel, Field, constr, validator


class ConcentratesBase(BaseModel):
    concentrate_id: int = Field(..., description="Unique identifier for the concentrate")
    cultivator: constr = Field(..., description="Name of the cultivator")
    strain: constr = Field(..., description="Name of the strain")
    is_mystery: bool = Field(..., description="Indicates if the concentrate is a mystery product")
    card_path: constr = Field(..., description="Path to the concentrate's image card")
    voting_open: bool = Field(True, description="Indicates if voting is open for this concentrate")

    @validator("cultivator", "strain", pre=True, always=True)
    def verify_string_and_capitalize_name(cls, v):
        return v.capitalize() if isinstance(v, str) else None

    @validator("cultivator", "strain", pre=True, always=True)
    def strip_whitespace(cls, v):
        return v.strip() if isinstance(v, str) else None

    class Config:
        from_attributes = True


class HiddenConcentrate(ConcentratesBase):
    pass
