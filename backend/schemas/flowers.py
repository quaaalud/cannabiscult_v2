#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov  5 16:47:38 2023

@author: dale
"""

from pydantic import BaseModel, constr, EmailStr, root_validator
from typing import List, Optional


class FlowersBase(BaseModel):
    flower_id: int
    cultivator: str
    strain: str
    is_mystery: bool
    card_path: str
    voting_open: bool = True
    product_type: str = 'flower'

    class Config:
        orm_mode = True


class HiddenFlower(FlowersBase):

    @root_validator(pre=True)
    def mask_cultivator(cls, values):
        is_mystery = values.get("is_mystery", False)
        if is_mystery:
            values["cultivator"] = "Hidden"
        return values


class FlowerDescriptionBase(BaseModel):
    flower_id: int
    description: constr(max_length=1500) = "Coming Soon"
    effects: constr(max_length=1500) = "Coming Soon"
    lineage: constr(max_length=1500) = "Coming Soon"
    terpenes_list: Optional[List[str]]
    cultivar_email: EmailStr

    class Config:
        orm_mode = True


class AddFlowerDescription(FlowerDescriptionBase):
    pass


class GetFlowerDescription(FlowerDescriptionBase):
    description_id: int
