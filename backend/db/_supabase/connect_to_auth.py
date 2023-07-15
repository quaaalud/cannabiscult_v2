#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jul  2 22:54:46 2023

@author: dale
"""

from db._supabase import supa_client, connect_to_auth
from schemas.users import UserCreate, UserLogin
from db.repository.users import add_user_to_supabase

class SupaAuth:
    
    _client = supa_client.return_created_client()

    @classmethod
    def create_new_supabase_user(cls, user: UserCreate):    
        return add_user_to_supabase(
            user,
            cls._client
        )
      
    @classmethod
    def login_supabase_user_with_password(cls, user: UserLogin):
        return cls._client.auth.sign_in_with_password(
            {
                "email": user.email, 
                "password": user.password
            }
        )
    
    @classmethod
    def refresh_current_user_session(cls):    
        return cls._client.auth.refresh_session()
       

if __name__ == '__main__':
    print(SupaAuth._client)