#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 30 22:04:15 2023

@author: dale
"""

from pydantic import BaseModel


class MysteryEdibleBase(BaseModel):
    cultivator: str 
    strain: str
    card_path: str
    
    
class Vivid_Edible_Base(BaseModel):
    vivid_edible_id: int
    strain: str
    card_path: str
    
    class Config():
        from_attributes = True
    
class Get_Vivid_Edible(Vivid_Edible_Base):
    pass
    
    