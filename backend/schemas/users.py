#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 10 20:51:36 2023

@author: dale
"""

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    username: str
    email : EmailStr
    password : str
    name: str
    zip_code: str
    password : str
    agree_tos = bool
    can_vote = bool
    is_superuser = bool
    

class ShowUser(BaseModel):
    username : str 
    can_vote : bool

    class Config():
        orm_mode = True

