#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jul  2 22:55:43 2023

@author: dale
"""

from core.config import settings
from supabase import create_client, Client


def return_created_client(
    url: str = settings.SUPA_STORAGE_URL, key: str = settings.SUPA_PRIVATE_KEY
) -> Client:
    return create_client(url, key)


def get_cc_bucket():
    client = return_created_client()
    return client.storage.get_bucket(
        settings.POSTGRES_DB,
    )


def get_signed_url_from_storage(file_path: str, life_span: int = 6000):
    client = return_created_client()
    return (
        client.storage.from_(settings.POSTGRES_DB)
        .create_signed_url(file_path, life_span)
        .get("signedURL")
    )


if __name__ == "__main__":
    pass
