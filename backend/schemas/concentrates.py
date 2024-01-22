#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov  5 16:47:38 2023

@author: dale
"""

from pydantic import BaseModel, Field, constr


class ConcentratesBase(BaseModel):
    concentrate_id: int = Field(..., description="Unique identifier for the concentrate")
    cultivator: constr = Field(..., description="Name of the cultivator")
    strain: constr = Field(..., description="Name of the strain")
    is_mystery: bool = Field(..., description="Indicates if the concentrate is a mystery product")
    card_path: constr = Field(..., description="Path to the concentrate's image card")
    voting_open: bool = Field(True, description="Indicates if voting is open for this concentrate")

    class Config:
        from_attributes = True


class HiddenConcentrate(ConcentratesBase):
    pass
