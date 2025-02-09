#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep  4 17:26:25 2023

@author: dale
"""

from pathlib import Path
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Union
from db.session import get_supa_db, get_db
from db.base import Flower_Ranking
from schemas.flowers import (
    FlowersBase,
    GetFlowerWithDescription,
    CreateFlowerRanking,
    FlowerReviewResponse,
    GetFlowerRanking,
    FlowerRankingValuesSchema,
)
from schemas.product_types import RatingsErrorResponse
from db.repository.flowers import (
    get_flower_and_description,
    get_flower_and_description_by_id,
    get_review_data_and_path,
    get_flower_data_and_path,
    update_or_create_flower_ranking,
    return_average_flower_ratings,
)
from db._supabase.connect_to_storage import return_image_url_from_supa_storage

router = APIRouter()


@router.get("/", response_model=FlowersBase)
async def query_flower_by_strain(
    strain: str = Query(None, alias="strain"), db: Session = Depends(get_db)
) -> Dict[str, Any]:
    return get_flower_data_and_path(db, strain)


@router.get("/description", response_model=GetFlowerWithDescription)
async def query_flower_description_by_strain(
    strain: str = Query(None, alias="strain"),
    cultivator: str = Query(None, alias="cultivator"),
    flower_id: str = Query(None, alias="flower_id"),
    cultivar_email: str = Query("aaron.childs@thesocialoutfitus.com", alias="cultivar"),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    flower_data = None
    if flower_id:
        flower_data = get_flower_and_description_by_id(db, flower_id, cultivar_email)
    elif cultivator and strain:
        flower_data = await get_flower_and_description(db, strain, cultivar_email, cultivator)
    if flower_data:
        return flower_data
    else:
        raise HTTPException(status_code=404, detail="Flower or description not found")


@router.get("/get_flower_from_strain_and_cultivator", response_model=FlowerReviewResponse)
async def return_selected_review(strain_selected: str, cultivator_selected: str, db: Session = Depends(get_supa_db)):
    return get_review_data_and_path(db, cultivator_selected, strain_selected)


@router.post("/ranking", response_model=GetFlowerRanking)
async def submit_flower_ranking(ranking: CreateFlowerRanking, db: Session = Depends(get_db)) -> Flower_Ranking:
    submitted_ranking = update_or_create_flower_ranking(ranking_dict=ranking, db=db)
    return submitted_ranking


@router.get("/get_top_flower_strains", response_model=List[GetFlowerWithDescription])
async def get_top_strains(db: Session = Depends(get_supa_db)):
    avg_ratings = await return_average_flower_ratings(db)
    scored_strains = []
    for strain in avg_ratings:
        overall_score = sum(filter(None, strain[-6:])) / 6 if strain[-6:] else 0
        strain_data = {
            "strain": strain.strain,
            "cultivator": strain.cultivator,
            "flower_id": strain.flower_id,
            "description_id": strain.description_id,
            "description_text": strain.description_text,
            "effects": strain.effects,
            "lineage": strain.lineage,
            "terpenes_list": strain.terpenes_list,
            "strain_category": strain.strain_category,
            "cultivar": strain.cultivar,
            "username": strain.username,
            "voting_open": strain.voting_open,
            "is_mystery": strain.is_mystery,
            "product_type": strain.product_type,
            "overall_score": round(overall_score, 2),
            "url_path": strain.card_path,
        }
        scored_strains.append(strain_data)
    scored_strains.sort(key=lambda x: x["overall_score"], reverse=True)
    return_strains = scored_strains[:3]
    for strain in return_strains:
        strain["url_path"] = return_image_url_from_supa_storage(str(Path(strain["url_path"])))
    return scored_strains[:3]


@router.get("/get_top_rated_flower_strains", response_model=List)
async def get_top_flower_strains(
    strains_count: int = Query(5, alias="strain_count"), db: Session = Depends(get_supa_db)
):
    try:
        avg_ratings = await return_average_flower_ratings(db)
        scored_strains = []
        for strain in avg_ratings:
            overall_score = sum(filter(None, strain[-6:])) / 6 if strain[-6:] else 0
            strain_data = {
                "strain": strain.strain,
                "cultivator": strain.cultivator,
                "flower_id": strain.flower_id,
                "description_id": strain.description_id,
                "description_text": strain.description_text,
                "effects": strain.effects,
                "lineage": strain.lineage,
                "terpenes_list": strain.terpenes_list,
                "strain_category": strain.strain_category,
                "cultivar": strain.cultivar,
                "username": strain.username,
                "voting_open": strain.voting_open,
                "is_mystery": strain.is_mystery,
                "product_type": strain.product_type,
                "overall_score": round(overall_score, 2),
                "url_path": strain.card_path,
            }
            scored_strains.append(strain_data)
        scored_strains.sort(key=lambda x: x["overall_score"], reverse=True)
        return_strains = scored_strains[:strains_count]
        for strain in return_strains:
            strain["url_path"] = return_image_url_from_supa_storage(str(Path(strain["url_path"])))
        return return_strains
    except Exception as e:
        raise e


@router.get(
    "/get_strain_ratings_by_id/{flower_id}/", response_model=Union[FlowerRankingValuesSchema, RatingsErrorResponse]
)
async def get_strain_ratings_by_id(flower_id: int, db: Session = Depends(get_supa_db)):
    avg_ratings = (
        db.query(
            func.avg(Flower_Ranking.appearance_rating),
            func.avg(Flower_Ranking.smell_rating),
            func.avg(Flower_Ranking.flavor_rating),
            func.avg(Flower_Ranking.effects_rating),
            func.avg(Flower_Ranking.harshness_rating),
            func.avg(Flower_Ranking.freshness_rating),
        )
        .filter(Flower_Ranking.flower_ranking_id == flower_id)
        .first()
    )
    if not avg_ratings or any(rating is None for rating in avg_ratings):
        return {"strain": "no match found", "message": "Flower not found or incomplete data for rankings."}
    return {
        "flower_ranking_id": int(flower_id),
        "overall_score": round(sum(avg_ratings) / 6, 2),
        "appearance_rating": avg_ratings[0],
        "smell_rating": avg_ratings[1],
        "flavor_rating": avg_ratings[2],
        "effects_rating": avg_ratings[3],
        "harshness_rating": avg_ratings[4],
        "freshness_rating": avg_ratings[5],
    }
