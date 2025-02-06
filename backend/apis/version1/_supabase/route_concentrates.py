#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep  4 17:26:25 2023

@author: dale
"""

from fastapi import APIRouter
from sqlalchemy.orm import Session
from fastapi import Depends, Query, HTTPException
from typing import List, Dict, Any
from db.session import get_db
from db.repository.concentrates import (
    get_concentrate_and_description,
    get_concentrate_data_and_path,
    get_vibe_concentrate_strains,
    get_concentrate_by_strain_and_cultivator,
)


router = APIRouter()


@router.get("/get-concentrate", response_model=Dict[str, Any])
async def query_concentrate_by_strain(
    strain: str = Query(None, alias="strain"), db: Session = Depends(get_db)
) -> Dict[str, Any]:
    return get_concentrate_data_and_path(
        db,
        strain,
    )


@router.get("/get_concentrate_review", response_model=Dict[str, Any])
async def query_concentrate_by_strain_and_cultivator(
    strain: str = Query(None, alias="strain"),
    cultivator: str = Query(None, alias="cultivator"),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    concentrate_dict = await get_concentrate_by_strain_and_cultivator(
        db,
        strain,
        cultivator,
    )
    return concentrate_dict


@router.get("/get-vibe-concentrate", response_model=Dict[str, Any])
async def query_vibe_concentrate_by_strain(
    strain: str = Query(None, alias="strain"), db: Session = Depends(get_db)
) -> Dict[str, Any]:
    return get_concentrate_data_and_path(
        db,
        strain_select=strain,
    )


@router.get("/get-vibe-concentrate-strains", response_model=List[str])
async def query_vibe_concentrate_strains(db: Session = Depends(get_db)) -> List[str]:
    return get_vibe_concentrate_strains(db)


@router.get("/get_concentrate_description", response_model=Dict[str, Any])
async def query_concentrate_description_by_strain(
    strain: str = Query(None, alias="strain"),
    cultivator: str = Query(None, alias="cultivator"),
    cultivar_email: str = Query("aaron.childs@thesocialoutfitus.com", alias="cultivar"),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    concentrate_data = await get_concentrate_and_description(db, strain, cultivator, cultivar_email)
    if concentrate_data:
        return concentrate_data
    else:
        raise HTTPException(status_code=404, detail="Concentrate or description not found")
