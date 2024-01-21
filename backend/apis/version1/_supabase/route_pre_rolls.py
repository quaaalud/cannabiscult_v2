#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan 21 14:26:47 2024

@author: dale
"""

from fastapi import APIRouter
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import Depends
from typing import Dict, Any
from db.session import get_db
from db.models import pre_rolls
from db.repository import pre_rolls
from schemas import pre_rolls


router = APIRouter()
