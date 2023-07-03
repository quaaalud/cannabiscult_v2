#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul  3 15:44:00 2023

@author: dale
"""

from pydantic import BaseModel


class FlowerReviewCreate(BaseModel):
    cultivator: str
    strain: str
    overall: float
    structure: float
    nose: float
    flavor: float
    effects: float
    vote_count: int
    card_path: str
    

class ShowSubscriber(BaseModel):
    cultivator: str
    strain: str
    overall: float
    structure: float
    nose: float
    flavor: float
    effects: float
    vote_count: int
    card_path: str

    class Config():
        orm_mode = True