#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov  5 16:47:38 2023

@author: dale
"""

from pydantic import BaseModel, Json, Field
from typing import Optional


class ProductTypes(BaseModel):
    product_type: str = Field(..., description="Type of the product")
    extra_data: Optional[Json] = Field(None, description="Additional data in JSON format, optional")

    class Config:
        from_attributes = True
        exclude_unset = True
        populate_by_name = True
        strip_whitespace = True
