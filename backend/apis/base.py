#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 10 21:36:01 2023

@author: dale
"""

from fastapi import APIRouter
import route_general_pages
import route_subscribers
import route_users
from _supabase import route_flowers
from _supabase import route_concentrates
from _supabase import route_edibles
from _supabase import route_mystery_voters
from _supabase import route_searches
from _supabase import route_pre_rolls
from _supabase import route_strain_submissions
from _supabase import route_images
from middleware import mystery_pack_route_handler

api_router = APIRouter()
api_router.include_router(route_general_pages.general_pages_router, prefix="", tags=["general_pages"])
api_router.include_router(route_subscribers.router, prefix="/subscribers", tags=["subscriber"])
api_router.include_router(route_users.router, prefix="/users", tags=["user"])
api_router.include_router(route_flowers.router, prefix="/flowers", tags=["flowers"])
api_router.include_router(route_edibles.router, prefix="/edibles", tags=["edibles"])
api_router.include_router(route_pre_rolls.router, prefix="/prerolls", tags=["prerolls"])
api_router.include_router(route_concentrates.router, prefix="/concentrates", tags=["concentrate_reviews"])
api_router.include_router(route_mystery_voters.router, prefix="/mystery_voters", tags=["mystery_voters"])
api_router.include_router(route_searches.router, prefix="/search", tags=["search"])
api_router.include_router(route_strain_submissions.router, prefix="/submit", tags=["submit"])
api_router.include_router(route_images.router, prefix="/images", tags=["images"])
