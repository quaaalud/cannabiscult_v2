#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 11 21:55:38 2023

@author: dale
"""

from pydantic import BaseModel, EmailStr


class MysteryVoterCreate(BaseModel):
    email : EmailStr  
    name : str
    zip_code : str
    phone : str
    

class ShowMysteryVoter(BaseModel):
    email : EmailStr

    class Config():
        from_attributes = True