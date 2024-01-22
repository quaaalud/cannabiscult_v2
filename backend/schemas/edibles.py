#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 30 22:04:15 2023

@author: dale
"""


from pydantic import BaseModel, Field, constr


class EdiblesBase(BaseModel):
    cultivator: constr = Field(..., description="Name of the cultivator")
    strain: constr = Field(..., description="Name of the strain")
    card_path: constr = Field(..., description="Path to the edible's image card")

    class Config:
        from_attributes = True


class Edible(EdiblesBase):
    pass


class MysteryEdibleBase(EdiblesBase):
    pass


class Vivid_Edible_Base(BaseModel):
    vivid_edible_id: int = Field(..., description="Unique identifier for the Vivid edible")
    strain: constr = Field(..., description="Name of the strain")
    card_path: constr = Field(..., description="Path to the Vivid edible's image card")

    class Config:
        from_attributes = True


class Get_Vivid_Edible(Vivid_Edible_Base):
    pass


class Vibe_Edible_Base(EdiblesBase):
    pass


class Get_Vibe_Edible(Vibe_Edible_Base):
    pass
