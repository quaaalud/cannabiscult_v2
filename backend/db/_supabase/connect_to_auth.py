#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jul  2 22:54:46 2023

@author: dale
"""

import sys
from pathlib import Path

if str(Path(__file__).parents[2]) not in sys.path:
    sys.path.append(str(Path(__file__).parents[2]))

from db._supabase import supa_client
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
        if not cls._client.auth.get_session():
            return cls._client.auth.sign_in_with_password(
                {
                    "email": user.email,
                    "password": user.password
                }
            )
        return cls.refresh_current_user_session()
      
    @classmethod
    def get_existing_session(cls):
        return cls._client.auth.get_session()
      
    @classmethod
    def logout_current_user_session(cls):
        try:
            return cls._client.auth.sign_out()
        except:
            pass

    @classmethod
    def refresh_current_user_session(cls):
        return cls._client.auth.refresh_session()
      
    @classmethod
    def return_current_user_email(cls):
        logged_in_user = cls.get_existing_session()
        if logged_in_user:
            user_email = logged_in_user.dict()['user']['email']
            return user_email
        else:
            return None
            


if __name__ == '__main__':
    
    print(SupaAuth.return_current_user_email())
