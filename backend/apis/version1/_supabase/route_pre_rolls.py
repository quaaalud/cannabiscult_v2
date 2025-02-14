#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan 21 14:26:47 2024

@author: dale
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Body, Path
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional, List
from db.session import get_db
from db.repository import pre_rolls as pre_rolls_repo
from schemas import pre_rolls as pre_rolls_schemas


router = APIRouter()


@router.get("/get_pre_roll_data", response_model=Optional[Dict[str, Any]])
async def query_pre_roll_by_strain(
    strain: str = Query(..., description="The strain of the pre-roll to query"),
    db: Session = Depends(get_db),
) -> Optional[Dict[str, Any]]:
    pre_roll_data = await pre_rolls_repo.get_pre_roll_data_and_path(db, strain)
    if pre_roll_data:
        return pre_roll_data
    else:
        raise HTTPException(
            status_code=404, detail="Pre-roll data not found for the specified strain"
        )


@router.get("/get_pre_roll_by_strain_and_cultivator", response_model=Optional[Dict[str, Any]])
async def query_pre_roll_by_strain_and_cultivator(
    strain: str = Query(..., description="The strain of the pre-roll to query"),
    cultivator: str = Query(..., description="The cultivator of the pre-roll to query"),
    db: Session = Depends(get_db),
) -> Optional[Dict[str, Any]]:
    pre_roll_data = await pre_rolls_repo.get_pre_roll_by_strain_and_cultivator(
        db, strain, cultivator
    )
    if pre_roll_data:
        return pre_roll_data
    else:
        raise HTTPException(
            status_code=404,
            detail="Pre-roll data not found for the specified strain and cultivator",
        )


@router.get("/get_pre_roll_strains_by_cultivator", response_model=Optional[List[str]])
async def query_pre_roll_strains_by_cultivator(
    cultivator: str = Query(..., description="The cultivator of the pre-rolls to query"),
    db: Session = Depends(get_db),
) -> Optional[List[str]]:
    strains = await pre_rolls_repo.get_pre_roll_strains_by_cultivator(db, cultivator)
    if strains:
        return strains
    else:
        raise HTTPException(
            status_code=404, detail=f"Strains not found for the specified cultivator: {cultivator}"
        )


@router.get("/get_pre_roll_and_description", response_model=Optional[Dict[str, Any]])
async def query_pre_roll_and_description(
    strain: str = Query(
        ...,
        description="The strain of the pre-roll to query",
        alias="strain",
    ),
    cultivator: str = Query(
        None, description="The cultivator of the pre-roll to query", alias="cultivator"
    ),
    cultivar_email: str = Query(
        "aaron.childs@thesocialoutfitus.com",
        description="Email of the cultivar",
        alias="connoisseur",
    ),
    db: Session = Depends(get_db),
) -> Optional[Dict[str, Any]]:
    pre_roll_data = await pre_rolls_repo.get_pre_roll_and_description(
        db, strain, cultivar_email, cultivator
    )
    if pre_roll_data:
        return pre_roll_data
    else:
        raise HTTPException(
            status_code=404,
            detail="Pre-roll data or description not found for the specified query parameters",
        )


@router.post("/ranking", response_model=Any)
async def update_or_create_pre_roll_ranking_route(
    ranking_data: pre_rolls_schemas.PreRollRankingSchema = Body(...), db: Session = Depends(get_db)
):
    try:
        updated_or_new_ranking = await pre_rolls_repo.update_or_create_pre_roll_ranking(
            ranking_data, db
        )
        return updated_or_new_ranking
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/get_pre_roll_ranking", response_model=Dict[str, Any])
async def get_pre_roll_ranking_data_and_path_from_id_route(
    id_selected: int = Query(..., alias="pre_roll_id"), db: Session = Depends(get_db)
) -> Dict[str, Any]:
    ranking_data = await pre_rolls_repo.get_pre_roll_ranking_data_and_path_from_id(db, id_selected)
    if ranking_data:
        return ranking_data
    else:
        raise HTTPException(
            status_code=404, detail="Pre-roll ranking not found for the specified ID"
        )


@router.get("/get_all_strains", response_model=List[str])
async def get_all_strains_route(db: Session = Depends(get_db)) -> List[str]:
    strains = await pre_rolls_repo.get_all_strains(db)
    return strains


@router.get("/get_strains_for_cultivator", response_model=List[str])
async def get_strains_for_cultivator_route(
    cultivator: str = Query(..., description="Cultivator to fetch strains for"),
    db: Session = Depends(get_db),
) -> List[str]:
    strains = await pre_rolls_repo.get_all_strains_for_cultivator(cultivator, db)
    return strains


@router.get("/get_all_cultivators", response_model=List[str])
async def get_all_cultivators_route(db: Session = Depends(get_db)) -> List[str]:
    cultivators = await pre_rolls_repo.get_all_cultivators(db)
    return cultivators


@router.get("/get_cultivators_for_strain", response_model=List[str])
async def get_cultivators_for_strain_route(
    strain: str = Query(None, alias="strain", description="Strain to fetch cultivators for"),
    db: Session = Depends(get_db),
) -> List[str]:
    cultivators = await pre_rolls_repo.get_all_cultivators_for_strain(strain, db)
    return cultivators


@router.get("/get_top_pre_roll_strains", response_model=List[Dict])
async def get_top_pre_roll_strains_route(db: Session = Depends(get_db)) -> List[Dict]:
    top_strains = await pre_rolls_repo.get_top_pre_roll_strains(db)
    return top_strains


@router.get("/get_pre_roll_rating_by_id/{pre_roll_id}", response_model=Optional[Dict[str, Any]])
async def get_pre_roll_ratings_by_id_path_route(
    pre_roll_id: int = Path(..., description="The ID of the pre-roll to retrieve ratings for"),
    db: Session = Depends(get_db),
) -> Optional[Dict[str, float]]:
    pre_roll_ratings = await pre_rolls_repo.get_pre_roll_ratings_by_id(pre_roll_id, db)
    if pre_roll_ratings:
        return pre_roll_ratings
    else:
        raise HTTPException(
            status_code=404,
            detail="Pre-roll ratings not found or incomplete data for the specified ID",
        )
