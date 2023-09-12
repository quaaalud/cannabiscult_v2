#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep  4 17:19:02 2023

@author: dale
"""

from pydantic import BaseModel
from typing import List


class ConcentrateReviewCreate(BaseModel):
    cultivator: str
    strain: str
    overall: float
    structure: float
    nose: float
    flavor: float
    effects: float
    vote_count: int
    card_path: str
    
    
class ConcentrateReviewUpdate(BaseModel):
    review_id: int
    structure: float
    nose: float
    flavor: float
    effects: float
    

class ConcentrateFlowerReview(BaseModel):
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