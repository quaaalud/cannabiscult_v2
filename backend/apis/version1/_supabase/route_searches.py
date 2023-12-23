#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 22 20:27:46 2023

@author: dale
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.session import get_db
from typing import List
from schemas.search_class import SearchResultItem
from db.repository.search_class import search_strain


router = APIRouter()


@router.get("/all/{search_term}", response_model=List[SearchResultItem])
async def get_search_matches(search_term: str, db: Session = Depends(get_db)):
    if not search_term or len(search_term) < 3:
        return []
    results = await search_strain(db, search_term)
    if not results:
        raise HTTPException(status_code=404, detail="No matches found")
    return results
