#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar  5 21:10:59 2023

@author: dale
"""

from fastapi import APIRouter
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates


templates = Jinja2Templates(directory="templates")
general_pages_router = APIRouter()


@general_pages_router.get("/")
async def home(request: Request):
	return templates.TemplateResponse(
        "general_pages/homepage.html",
        {"request":request}
        )