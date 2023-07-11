#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jul  2 22:54:46 2023

@author: dale
"""

from db._supabase import supa_client
import base64

def get_reviews_list() -> list[dict]:    
    supa_client.return_created_client()
    res = supabase.auth.sign_up({
      "email": 'example@email.com',
      "password": 'example-password',
      "options": {
        "data": {
          "first_name": 'John',
          "age": 27,
        }
      }
    })
    return bucket.list(path=folder_path)
       

def get_image_from_results(file_path: str):
    bucket = supa_client.get_cc_bucket()
    img_bytes = bucket.download(
        path=file_path
    )
    return base64.b64encode(img_bytes).decode()