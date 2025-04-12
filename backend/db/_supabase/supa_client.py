#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jul  2 22:55:43 2023

@author: dale
"""

import time
from functools import wraps
from core.config import settings
from supabase import create_client, Client


def return_created_client(url: str = settings.SUPA_STORAGE_URL, key: str = settings.SUPA_PRIVATE_KEY) -> Client:
    return create_client(url, key)


def get_cc_bucket(bucket_name: str = settings.POSTGRES_DB):
    client = return_created_client()
    return client.storage.get_bucket(bucket_name)


def ttl_cache(ttl: int):
    def decorator(func):
        cache = {}

        @wraps(func)
        def wrapper(*args, **kwargs):
            key = args + tuple(sorted(kwargs.items()))
            now = time.time()
            if key in cache:
                result, timestamp = cache[key]
                if now - timestamp < ttl:
                    return result
            result = func(*args, **kwargs)
            cache[key] = (result, now)
            return result
        return wrapper
    return decorator


@ttl_cache(ttl=2900)
def get_cached_signed_url_from_storage(file_path: str, life_span: int = 60) -> str:
    default_img = "https://members.cannabiscult.co/storage/v1/object/public/cannabiscult/reviews/Connoisseur_Pack/CP_strains.webp"
    client = return_created_client()
    try:
        return client.storage.from_(settings.POSTGRES_DB).create_signed_url(file_path, life_span).get("signedURL")
    except Exception:
        return default_img


def get_signed_url_from_storage(file_path: str, life_span: int = 6000) -> str:
    file_path = file_path.replace("'", "")
    return get_cached_signed_url_from_storage(file_path, life_span)


if __name__ == "__main__":
    pass
