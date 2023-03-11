#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar  5 21:10:59 2023

@author: dale
"""

from pathlib import Path
from fastapi import APIRouter
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates


templates_dir = Path(
    Path(__file__).parents[2],
    'templates',
)

templates = Jinja2Templates(directory=str(templates_dir))
general_pages_router = APIRouter()


@general_pages_router.get("/")
async def home(request: Request):
    return templates.TemplateResponse(
        str(
            Path(
                'general_pages', 
                'homepage.html'
            )
        ), 
        {"request":request},
    )