#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 30 22:14:44 2023

@author: dale
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Dict, List
from db.session import get_db
from db.repository.mystery_edibles import get_edible_data_and_path
from db.models.mystery_edibles import MysteryEdible

router = APIRouter()


@router.post("/get-all-mystery-edibles", response_model=List[str])
async def get_all_mystery_edibles(
        db: Session = Depends(get_db)
) -> List[str]:
    all_strains = db.query(MysteryEdible.strain).all()
    return sorted(set([result[0] for result in all_strains]))


@router.get("/get-mystery-edible")
async def get_return_selected_mystery_edible(
    strain_selected: str = Query(None, alias="strain_selected"),
    db: Session = Depends(get_db)
) -> Dict[str]:
    return get_edible_data_and_path(
        db,
        strain_select=strain_selected,
    )
  
@router.post("/get-mystery-edible")  
async def post_return_selected_mystery_edible(
        strain_selected: str,
        db: Session = Depends(get_db)
) -> Dict[str]:
    return get_edible_data_and_path(
        db,
        strain_select=strain_selected,
    )
