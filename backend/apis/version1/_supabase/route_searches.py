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
from db.models.flowers import Flower
from db.models.concentrates import Concentrate
from db.models.edibles import Edible
from db.repository.search_class import (
    search_strain,
    get_all_product_types,
    get_cultivators_by_product_type,
    get_strains_by_cultivator,
)


router = APIRouter()


@router.get("/all/{search_term}", response_model=List[SearchResultItem])
async def get_search_matches(search_term: str, db: Session = Depends(get_db)):
    if not search_term or len(search_term) < 3:
        return []
    results = await search_strain(db, search_term)
    if not results:
        raise HTTPException(status_code=404, detail="No matches found")
    return results


@router.get("/product-types", response_model=List[str])
async def get_product_types(db: Session = Depends(get_db)):
    try:
        product_types = await get_all_product_types(db)
        if not product_types:
            raise HTTPException(status_code=404, detail="No product types found")
        return product_types
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cultivators/{product_type}", response_model=List[str])
async def get_cultivators(product_type: str, db: Session = Depends(get_db)):
    product_type_to_model = {
        "Flower": Flower,
        "Concentrate": Concentrate,
        "Edible": Edible,
        # Add other product types here
    }

    model = product_type_to_model.get(product_type)
    if not model:
        raise HTTPException(status_code=404, detail="Product type not found")

    cultivators = get_cultivators_by_product_type(db, model)
    if cultivators is None:
        raise HTTPException(status_code=500, detail="An error occurred")

    return cultivators


@router.get("/strains/{product_type}/{cultivator}", response_model=List[str])
async def get_strains(product_type: str, cultivator: str, db: Session = Depends(get_db)):
    product_type_to_model = {
        "Flower": Flower,
        "Concentrate": Concentrate,
        "Edible": Edible,
        # Add other product types here
    }

    model = product_type_to_model.get(product_type)
    if not model:
        raise HTTPException(status_code=404, detail="Product type not found")

    strains = get_strains_by_cultivator(db, model, cultivator)
    if strains is None:
        raise HTTPException(status_code=500, detail="An error occurred")

    return strains
