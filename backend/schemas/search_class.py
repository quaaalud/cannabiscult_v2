#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 22 20:12:30 2023

@author: dale
"""

from pydantic import BaseModel
from typing import List


class SearchResultItem(BaseModel):
    cultivator: str
    strain: str
    type: str
    url_path: str


class SearchResults(BaseModel):
    results: List[SearchResultItem]
