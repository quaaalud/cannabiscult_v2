#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 30 22:14:44 2023

@author: dale
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Dict, List, Any
from db.session import get_db
from db.repository.edibles import (
    get_edible_data_and_path,
    get_vibe_edible_data_by_strain,
    create_edible_ranking,
    create_vibe_edible_ranking,
)
from schemas.edibles import CreateEdibleRanking, CreateVibeEdibleRanking
from db.base import Edible, Edible_Ranking, Vibe_Edible_Ranking

router = APIRouter()


@router.post("/get-all-mystery-edibles", response_model=List[str])
async def get_all_mystery_edibles(db: Session = Depends(get_db)) -> List[str]:
    all_strains = db.query(Edible.strain).all()
    return sorted(set([result[0] for result in all_strains]))


@router.get("/get-mystery-edible", response_model=Dict[str, Any])
async def get_return_selected_mystery_edible(
    strain_selected: str = Query(None, alias="strain_selected"), db: Session = Depends(get_db)
) -> Dict[str, Any]:
    return get_edible_data_and_path(
        db,
        strain_select=strain_selected,
    )


@router.post("/get-mystery-edible", response_model=Dict[str, Any])
async def post_return_selected_mystery_edible(strain_selected: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    return get_edible_data_and_path(
        db,
        strain_select=strain_selected,
    )


@router.get("/get-vibe-edible", response_model=Dict[str, Any])
async def query_vibe_edible_data_by_strain(
    edible_strain: str = Query(None, alias="edible_strain"), db: Session = Depends(get_db)
) -> Dict[str, Any]:
    return get_vibe_edible_data_by_strain(
        db,
        edible_strain=edible_strain,
    )


@router.post("/submit-mystery-edible-ranking", response_model=None)
def submit_mystery_edible_ranking(
    edible_ranking: CreateEdibleRanking, db: Session = Depends(get_db)
) -> Edible_Ranking:
    submitted_ranking = create_edible_ranking(edible_ranking=edible_ranking, db=db)
    return submitted_ranking


@router.post("/submit-vibe-edible-ranking", response_model=None)
def submit_vibe_edible_ranking(
    edible_ranking: CreateVibeEdibleRanking, db: Session = Depends(get_db)
) -> Vibe_Edible_Ranking:
    submitted_ranking = create_vibe_edible_ranking(edible_ranking=edible_ranking, db=db)
    return submitted_ranking
