#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 10 20:51:36 2023

@author: dale
"""

from typing import Optional
from pydantic import BaseModel,EmailStr


class UserCreate(BaseModel):
    username: str
    email : EmailStr
    password : str
    

class ShowUser(BaseModel):
    username : str 
    email : EmailStr
    is_active : bool


    class Config():
        orm_mode = True
