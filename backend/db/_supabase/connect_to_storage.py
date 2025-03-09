#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jul  2 22:54:46 2023

@author: dale
"""

from functools import lru_cache
from db._supabase import supa_client
import base64


def get_reviews_list() -> list[dict]:
    bucket = supa_client.get_cc_bucket()
    folder_path = "reviews"
    return bucket.list(path=folder_path)


def get_image_from_results(file_path: str):
    bucket = supa_client.get_cc_bucket()
    img_bytes = bucket.download(path=file_path)
    return base64.b64encode(img_bytes).decode()


def return_image_url_from_supa_storage(file_path: str):
    file_path = file_path.replace("'", "")
    return supa_client.get_signed_url_from_storage(file_path=file_path)
