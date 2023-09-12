#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul  3 15:44:00 2023

@author: dale
"""

from pydantic import BaseModel
from typing import List


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
    
    
class FlowerReviewUpdate(BaseModel):
    review_id: int
    structure: float
    nose: float
    flavor: float
    effects: float
    

class ShowFlowerReview(BaseModel):
    cultivator: str
    strain: str
    overall: float
    structure: float
    nose: float
    flavor: float
    effects: float
    vote_count: int
    card_path: str
    terpene_list: List[str]

    class Config:
        from_attributes = True