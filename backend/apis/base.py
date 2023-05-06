#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 10 21:36:01 2023

@author: dale
"""

import sys
from pathlib import Path

apis_dir = Path(__file__).parents[0]
backend_dir = Path(__file__).parents[1]
main_dir = Path(__file__).parents[2]
version_dir = Path(apis_dir, 'version1')

if str(main_dir) not in sys.path:
    sys.path.append(str(main_dir)) 
    
if str(backend_dir) not in sys.path:
    sys.path.append(str(backend_dir)) 
    
if str(apis_dir) not in sys.path:
    sys.path.append(str(apis_dir)) 
    
if str(version_dir) not in sys.path:
    sys.path.append(str(version_dir)) 

from fastapi import APIRouter
import route_general_pages
import route_subscribers


api_router = APIRouter()
api_router.include_router(
    route_general_pages.general_pages_router,
    prefix="",
    tags=["general_pages"]
)
api_router.include_router(
    route_subscribers.router,
    prefix="/subscribers",
    tags=["subscriber"]
)