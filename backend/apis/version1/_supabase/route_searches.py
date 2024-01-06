#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 22 20:27:46 2023

@author: dale
"""

import random
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.session import get_db
from typing import List, Optional, Any
from schemas.search_class import SearchResultItem
from db.models.flowers import Flower
from db.models.concentrates import Concentrate
from db.models.edibles import Edible, VibeEdible
from db.repository.search_class import (
    search_strain,
    get_all_product_types,
    get_cultivators_by_product_type,
    get_strains_by_cultivator,
    get_random_cultivator,
    get_random_strain,
)


router = APIRouter()


product_type_to_model = {
    "Flower": [Flower],
    "Concentrate": [Concentrate],
    "Edible": [Edible, VibeEdible],
    # Add other product types here
}


@router.get("/all/{search_term}", response_model=List[SearchResultItem])
async def get_search_matches(search_term: str, db: Session = Depends(get_db)):
    if not search_term or len(search_term) < 3:
        return []
    results = await search_strain(db, search_term)
    if not results:
        raise HTTPException(status_code=404, detail="No matches found")
    return results


@router.get("/product-types", response_model=List[Any])
async def get_product_types(db: Session = Depends(get_db)):
    try:
        product_types = await get_all_product_types(db)
        if not product_types:
            raise HTTPException(status_code=404, detail="No product types found")
        return product_types
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cultivators/{product_type}", response_model=List[Any], include_in_schema=False)
async def get_cultivators(
    product_type: str, product_type_dict=product_type_to_model, db: Session = Depends(get_db)
):
    models = product_type_dict.get(product_type)
    if not models:
        raise HTTPException(status_code=404, detail="Product type not found")

    all_cultivators = []
    for model in models:
        cultivators = get_cultivators_by_product_type(db, model)
        if cultivators:
            all_cultivators.extend(cultivators)

    if not all_cultivators:
        raise HTTPException(status_code=500, detail="An error occurred")

    return list(set(all_cultivators))


@router.get(
    "/strains/{product_type}/{cultivator}", response_model=List[str], include_in_schema=False
)
async def get_strains(
    product_type: str,
    cultivator: str,
    product_type_dict=product_type_to_model,
    db: Session = Depends(get_db),
):
    models = product_type_dict.get(product_type)
    if not models:
        raise HTTPException(status_code=404, detail="Product type not found")

    all_strains = []
    for model in models:
        strains = get_strains_by_cultivator(db, model, cultivator)
        if strains:
            all_strains.extend(strains)

    if not all_strains:
        raise HTTPException(status_code=500, detail="An error occurred")

    return all_strains


@router.get(
    "/random/cultivator/{product_type}", response_model=Optional[str], include_in_schema=False
)
async def get_random_cultivator_search(
    product_type: str, product_type_dict=product_type_to_model, db: Session = Depends(get_db)
):
    models = product_type_dict.get(product_type)
    if not models:
        raise HTTPException(status_code=404, detail="Product type not found")

    random_number = random.randint(0, 3)

    random_cultivator = get_random_cultivator(db, models[random_number])
    if not random_cultivator:
        raise HTTPException(status_code=404, detail="No cultivators found")

    return random_cultivator
