#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jul  2 22:54:46 2023

@author: dale
"""

from db._supabase import supa_client


def get_reviews_list() -> list[dict]:    
    bucket = supa_client.get_no_chalk_bucket()
    folder_path = 'reviews'
    return bucket.list(path=folder_path)
       

def get_image_from_results(file_name: str):
    file_path=f"reviews/{file_name}"
    bucket = supa_client.get_no_chalk_bucket()
    return bucket.download(
        path=file_path
    )