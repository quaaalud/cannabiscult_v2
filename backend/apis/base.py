#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 10 21:36:01 2023

@author: dale
"""

import sys
from pathlib import Path

apis_dir = Path(__file__).parents[0]
backend_dir = Path(__file__).parents[1]
main_dir = Path(__file__).parents[2]
version_dir = Path(apis_dir, 'version1')
supa_dir = Path(version_dir, '_supabase')

if str(main_dir) not in sys.path:
    sys.path.append(str(main_dir)) 
    
if str(backend_dir) not in sys.path:
    sys.path.append(str(backend_dir)) 
    
if str(apis_dir) not in sys.path:
    sys.path.append(str(apis_dir)) 
    
if str(version_dir) not in sys.path:
    sys.path.append(str(version_dir)) 
    
if str(supa_dir) not in sys.path:
    sys.path.append(str(supa_dir)) 

from fastapi import APIRouter
import route_general_pages
import route_subscribers
import route_users
from _supabase import route_flowers
from _supabase import route_concentrates
from _supabase import route_concentrate_rankings
from _supabase import route_edibles
from _supabase import route_flower_rankings
from _supabase import route_flower_reviews
from _supabase import route_flower_voting
from _supabase import route_mystery_flower_review
from _supabase import route_mystery_voters
from _supabase import route_edible_rankings
from _supabase import route_searches

api_router = APIRouter()
api_router.include_router(
    route_general_pages.general_pages_router,
    prefix="",
    tags=["general_pages"]
)
api_router.include_router(
    route_subscribers.router,
    prefix="/subscribers",
    tags=["subscriber"]
)
api_router.include_router(
    route_users.router,
    prefix="/users",
    tags=["user"]
)
api_router.include_router(
    route_flowers.router,
    prefix="/flowers",
    tags=["flowers"]
)
api_router.include_router(
    route_edibles.router,
    prefix="/edibles",
    tags=["edibles"]
)
api_router.include_router(
    route_concentrates.router,
    prefix="/concentrate_reviews",
    tags=["concentrate_reviews"]
)
api_router.include_router(
    route_concentrate_rankings.router,
    prefix="/concentrate_ranking",
    tags=["concentrate_ranking"]
)
api_router.include_router(
    route_flower_rankings.router,
    prefix="/flower_ranking",
    tags=["flower_ranking"]
)
api_router.include_router(
    route_flower_reviews.router,
    prefix="/flower_reviews",
    tags=["flower_reviews"]
)
api_router.include_router(
    route_flower_voting.router,
    prefix="/flower_voting",
    tags=["flower_voting"]
)
api_router.include_router(
    route_mystery_flower_review.router,
    prefix="/mystery_flower_review",
    tags=["mystery_flower_review"]
)
api_router.include_router(
    route_mystery_voters.router,
    prefix="/mystery_voters",
    tags=["mystery_voters"]
)
api_router.include_router(
    route_edible_rankings.router,
    prefix="/edible_rankings",
    tags=["edible_rankings"]
)
api_router.include_router(
    route_searches.router,
    prefix="/search",
    tags=["search"]
)
