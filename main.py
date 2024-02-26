#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar  5 21:13:44 2023

@author: dale
"""

import sys
from pathlib import Path

MAIN_DIR = Path(__file__).parent
BACKEND_DIR = Path(MAIN_DIR, "backend")
API_DIR = Path(BACKEND_DIR, "apis")
VERSION1_DIR = Path(API_DIR, "version1")
CORE_DIR = Path(BACKEND_DIR, "core")
TEMPLATES_DIR = Path(BACKEND_DIR, "templates")
STATIC_DIR = Path(BACKEND_DIR, "static")
DB_DIR = Path(BACKEND_DIR, "db")
MODELS_DIR = Path(DB_DIR, "models")
SUPA_DB = Path(DB_DIR, "_supabase")


if str(MAIN_DIR) not in sys.path:
    sys.path.append(str(MAIN_DIR))

if str(BACKEND_DIR) not in sys.path:
    sys.path.append(str(BACKEND_DIR))

if str(API_DIR) not in sys.path:
    sys.path.append(str(API_DIR))

if str(VERSION1_DIR) not in sys.path:
    sys.path.append(str(VERSION1_DIR))

if str(CORE_DIR) not in sys.path:
    sys.path.append(str(CORE_DIR))

if str(TEMPLATES_DIR) not in sys.path:
    sys.path.append(str(TEMPLATES_DIR))

if str(STATIC_DIR) not in sys.path:
    sys.path.append(str(STATIC_DIR))

if str(MODELS_DIR) not in sys.path:
    sys.path.append(str(MODELS_DIR))


from fastapi import FastAPI, Request, Response
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse
import os
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from core.config import settings
from apis.base import api_router, mystery_pack_route_handler
from fastapi.staticfiles import StaticFiles
from db.session import engine
from db.base import Base


def include_router(app):
    app.include_router(api_router)


def configure_static(app):
    global STATIC_DIR
    app.mount(
        str(STATIC_DIR),
        StaticFiles(directory=str(STATIC_DIR), follow_symlink=True),
        name="static",
    )


def create_tables():
    print("create_tables")
    Base.metadata.create_all(bind=engine)


def start_application():
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.PROJECT_VERSION,
        #        docs_url=None,
        #        redoc_url=None,
    )
    include_router(app)
    configure_static(app)
    create_tables()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    app.add_middleware(mystery_pack_route_handler.LegacyURLMiddleware)
    return app


app = start_application()
