#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov  5 16:47:38 2023

@author: dale
"""

from pydantic import BaseModel


class ConcentratesBase(BaseModel):
    concentrate_id: int
    cultivator: str 
    strain: str
    is_mystery: bool
    card_path: str
    voting_open: bool = True
    
    class Config():
        from_attributes = True
        
        
class HiddenConcentrate(ConcentratesBase):
    pass
    
