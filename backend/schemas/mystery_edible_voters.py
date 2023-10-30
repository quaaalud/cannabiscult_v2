#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 30 18:53:33 2023

@author: dale
"""

from pydantic import BaseModel, EmailStr
from typing import Optional


class MysteryEdibleVoterBase(BaseModel):
    email: str
    name: str
    zip_code: str
    phone: Optional[str] = None
    agree_tos: bool = True
    

class MysteryEdibleVoterCreate(MysteryEdibleVoterBase):
  
    class Config():  
      from_attributes = True
    

class ShowMysteryEdibleVoter(BaseModel):
    email: EmailStr

    class Config():
        from_attributes = True