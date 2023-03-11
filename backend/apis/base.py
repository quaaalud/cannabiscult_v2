#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 10 21:36:01 2023

@author: dale
"""

from fastapi import APIRouter
import sys
from pathlib import Path

api_dir = Path(__file__).parent
version_1_dir = Path(api_dir, 'version1')

if str(api_dir) not in sys.path:
    sys.path.append(str(api_dir))
    
if str(version_1_dir) not in sys.path:
    sys.path.append(str(version_1_dir))

from apis.version1 import route_general_pages
from apis.version1 import route_users


api_router = APIRouter()
api_router.include_router(
    route_general_pages.general_pages_router,
    prefix="",
    tags=["general_pages"]
)
api_router.include_router(
    route_users.router,
    prefix="/users",
    tags=["users"]
)