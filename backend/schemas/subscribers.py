#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr 15 20:04:19 2023

@author: dale
"""

from pydantic import BaseModel,EmailStr


class SubscriberCreate(BaseModel):
    email : EmailStr
    

class ShowSubscriber(BaseModel):
    email : EmailStr

    class Config():
        orm_mode = True