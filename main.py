#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar  5 21:13:44 2023

@author: dale
"""

import sys
from pathlib import Path

MAIN_DIR = Path(__file__).parent
BACKEND_DIR = Path(MAIN_DIR, 'backend')
API_DIR = Path(BACKEND_DIR, 'apis')
CORE_DIR = Path(BACKEND_DIR, 'core')
TEMPLATES_DIR = Path(BACKEND_DIR, 'templates')
STATIC_DIR = Path(BACKEND_DIR, 'static')

if str(MAIN_DIR) not in sys.path:
    sys.path.append(str(MAIN_DIR))
    
if str(BACKEND_DIR) not in sys.path:
    sys.path.append(str(BACKEND_DIR))
    
if str(API_DIR) not in sys.path:
    sys.path.append(str(API_DIR))
    
if str(CORE_DIR) not in sys.path:
    sys.path.append(str(CORE_DIR))
    
if str(TEMPLATES_DIR) not in sys.path:
    sys.path.append(str(TEMPLATES_DIR))
    
if str(STATIC_DIR) not in sys.path:
    sys.path.append(str(STATIC_DIR))
    

from fastapi import FastAPI
from core.config import settings
from fastapi.staticfiles import StaticFiles
from apis.general_pages.route_homepage import general_pages_router


def include_router(app):
    app.include_router(general_pages_router)
    

def configure_static(app):
    global STATIC_DIR
    app.mount(
        str(STATIC_DIR), 
        StaticFiles(directory=str(STATIC_DIR)),
        name="static"
    )


def start_application():
    app = FastAPI(title=settings.PROJECT_NAME,version=settings.PROJECT_VERSION)
    include_router(app)
    configure_static(app)
    return app 


app = start_application()
    