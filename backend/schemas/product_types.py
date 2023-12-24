#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov  5 16:47:38 2023

@author: dale
"""

from pydantic import BaseModel, Json
from typing import Optional


class FlowersBase(BaseModel):
    product_type: str
    extra_data: Optional[Json]

    class Config:
        orm_mode = True
