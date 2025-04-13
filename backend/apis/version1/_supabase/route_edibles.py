#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 30 22:14:44 2023

@author: dale
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import Dict, Any, Union, List, Optional
from db.session import get_db
from db.repository.edibles import (
    get_edible_data_and_path,
    get_vibe_edible_data_by_strain,
    create_vibe_edible_ranking,
    return_all_available_descriptions_from_strain_id,
    update_or_create_edible_ranking
)
from schemas.edibles import CreateEdibleRanking, CreateVibeEdibleRanking
from db.base import Edible_Ranking, Vibe_Edible_Ranking
from schemas.product_types import RatingsErrorResponse
from core.config import settings

router = APIRouter()


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


@router.post("/ranking", response_model=None, dependencies=[Depends(settings.jwt_auth_dependency)])
def submit_edible_ranking_route(
    edible_ranking: CreateEdibleRanking, db: Session = Depends(get_db)
) -> Edible_Ranking:
    submitted_ranking = update_or_create_edible_ranking(edible_ranking=edible_ranking, db=db)
    return submitted_ranking


@router.post("/submit-vibe-edible-ranking", response_model=None, dependencies=[Depends(settings.jwt_auth_dependency)])
def submit_vibe_edible_ranking(
    edible_ranking: CreateVibeEdibleRanking, db: Session = Depends(get_db)
) -> Vibe_Edible_Ranking:
    submitted_ranking = create_vibe_edible_ranking(edible_ranking=edible_ranking, db=db)
    return submitted_ranking


@router.get("/all_descriptions", response_model=List[Optional[Dict[str, Any]]])
async def return_all_available_descriptions_from_strain_id_route(
    edible_id: int, db: Session = Depends(get_db)
) -> List[Optional[Dict[str, Any]]]:
    all_descriptions = await return_all_available_descriptions_from_strain_id(db, int(edible_id))
    return all_descriptions


@router.get(
    "/get_strain_ratings_by_id/{edible_id}/", response_model=Union[Any, RatingsErrorResponse]
)
async def get_strain_ratings_by_id(edible_id: int, db: Session = Depends(get_db)):
    avg_ratings = (
        db.query(
            func.avg(Edible_Ranking.appearance_rating),
            func.avg(Edible_Ranking.flavor_rating),
            func.avg(Edible_Ranking.effects_rating),
            func.avg(Edible_Ranking.aftertaste_rating),
            func.avg(Edible_Ranking.feel_rating),
            func.avg(Edible_Ranking.chew_rating),
        )
        .filter(Edible_Ranking.edible_id == int(edible_id))
        .first()
    )
    if not avg_ratings or any(rating is None for rating in avg_ratings):
        return {"strain": "no match found", "message": "Edible not found or incomplete data for rankings."}
    return {
        "edible_ranking_id": int(edible_id),
        "overall_score": round(sum(avg_ratings) / 6, 2) if avg_ratings[0] else 0.0,
        "appearance_rating": avg_ratings[0] if avg_ratings[0] else 0.0,
        "flavor_rating": avg_ratings[1] if avg_ratings[1] else 0.0,
        "effects_rating": avg_ratings[2] if avg_ratings[2] else 0.0,
        "aftertaste_rating": avg_ratings[3] if avg_ratings[3] else 0.0,
        "feel_rating": avg_ratings[4] if avg_ratings[4] else 0.0,
        "chew_rating": avg_ratings[5] if avg_ratings[5] else 0.0,
    }
