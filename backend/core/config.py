#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar  5 21:17:34 2023

@author: dale
"""

import os
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()

class Settings:
    PROJECT_NAME:str = "Cannabis Cult"
    PROJECT_VERSION: str = "2.0.0"
    POSTGRES_USER: str = os.getenv('POSTGRES_USER')
    POSTGRES_PASSWORD: str = os.getenv('POSTGRES_PASSWORD')
    POSTGRES_SERVER: str = os.getenv('POSTGRES_SERVER')
    POSTGRES_PORT: str = os.getenv('POSTGRES_PORT')
    POSTGRES_DB: str = os.getenv('POSTGRES_DB')
    DATABASE_URL: str = f'postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}'
    
    SUPA_ID:str = os.getenv('SUPA_ID')
    SUPA_JWT:str = os.getenv('SUPA_JWT')
    SUPA_PORT:str = os.getenv('SUPA_PORT')
    SUPA_PASSWORD:str = os.getenv('SUPA_PASSWORD')
    SUPA_PRIVATE_KEY: str = os.getenv('SUPA_PRIVATE_KEY')
    SUPA_PUBLIC_KEY: str = os.getenv('SUPABASE_KEY')
    SUPA_STORAGE_URL: str = os.getenv('SUPA_STORAGE_URL')
    SUPA_URL: str = f'postgresql://postgres.{SUPA_ID}:{SUPA_PASSWORD}@aws-0-us-east-1.pooler.supabase.com:{SUPA_PORT}/postgres'
    ALGO: str = os.getenv('ALGO')
    PRIMARY_BUCKET: str = os.getenv('POSTGRES_DB')

class Config(BaseModel):
    SUPA_STORAGE_URL: str
    SUPA_PUBLIC_KEY: str
    ALGO: str
    PRIMARY_BUCKET: str = os.getenv('POSTGRES_DB')


settings = Settings()
