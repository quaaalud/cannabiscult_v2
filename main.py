#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar  5 21:13:44 2023

@author: dale
"""

from fastapi import FastAPI
from core.config import settings
from apis.general_pages.route_homepage import general_pages_router


def include_router(app):
	app.include_router(general_pages_router)


def start_application():
	app = FastAPI(title=settings.PROJECT_NAME,version=settings.PROJECT_VERSION)
	include_router(app)
	return app 


if __name__ == '__main__':
    app = start_application()