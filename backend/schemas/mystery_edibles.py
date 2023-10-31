#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 30 22:04:15 2023

@author: dale
"""

from pydantic import BaseModel, EmailStr
from typing import Optional


class MysteryEdibleBase(BaseModel):
    cultivator: str 
    strain: str
    card_path: str