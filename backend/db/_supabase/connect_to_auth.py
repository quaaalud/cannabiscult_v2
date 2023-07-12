#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jul  2 22:54:46 2023

@author: dale
"""

from db._supabase import supa_client

class SupaAuth:
    
    _client = supa_client.return_created_client()

    @classmethod
    def create_new_supabase_user(cls, user_dict):    
        return cls._client.auth.sign_up(user_dict)
    
    @classmethod
    def refresh_current_user_session(cls):    
        return cls._client.auth.refresh_session()
       

print(SupaAuth._client)