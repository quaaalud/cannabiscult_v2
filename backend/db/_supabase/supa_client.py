#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jul  2 22:55:43 2023

@author: dale
"""

from core.config import settings
from supabase import create_client, Client


def return_created_client(
        url: str = settings.SUPABASE_URL,
        key: str = settings.SUPA_PRIVATE_KEY) -> Client:
    return create_client(url, key)


def get_no_chalk_bucket():    
    client = return_created_client()
    return client.storage.get_bucket(
        settings.NO_CHALK_BUCKET, 
    ) 