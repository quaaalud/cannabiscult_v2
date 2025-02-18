#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep  4 17:26:25 2023

@author: dale
"""

from pathlib import Path
from fastapi import APIRouter
from sqlalchemy.orm import Session
from fastapi import Depends, Query, HTTPException
from typing import List, Dict, Any, Union, Optional
from db.session import get_db
from db.repository.concentrates import (
    get_concentrate_and_description,
    get_concentrate_data_and_path,
    get_vibe_concentrate_strains,
    get_concentrate_by_strain_and_cultivator,
    update_or_create_concentrate_ranking,
    create_vibe_concentrate_ranking,
    get_concentrate_rankings_by_id,
    return_average_concentrate_ratings,
    return_all_available_descriptions_from_strain_id,
)
from db.base import (
    Vibe_Concentrate_Ranking,
    Concentrate_Ranking,
)
from schemas.concentrates import (
    GetConcentrateWithDescription,
    CreateConcentrateRanking,
    ConcentrateRankingValuesSchema,
)
from schemas.product_types import RatingsErrorResponse
from db._supabase.connect_to_storage import return_image_url_from_supa_storage
from core.config import settings


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


@router.get("/get_concentrate_description", response_model=GetConcentrateWithDescription)
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


@router.get("/all_descriptions", response_model=List[Optional[Dict[str, Any]]])
async def return_all_available_descriptions_from_strain_id_route(
    concentrate_id: int, db: Session = Depends(get_db)
) -> List[Optional[Dict[str, Any]]]:
    all_descriptions = await return_all_available_descriptions_from_strain_id(db, int(concentrate_id))
    return all_descriptions


@router.post("/ranking", response_model=None, dependencies=[Depends(settings.jwt_auth_dependency)])
async def submit_concentrate_ranking(
    concentrate_ranking: CreateConcentrateRanking, db: Session = Depends(get_db)
) -> Concentrate_Ranking:
    return await update_or_create_concentrate_ranking(ranking=concentrate_ranking, db=db)


@router.post("/submit-vibe-concentrate-ranking", response_model=None)
async def submit_vibe_concentrate_ranking(
    ranking: CreateConcentrateRanking, db: Session = Depends(get_db)
) -> Vibe_Concentrate_Ranking:
    create_vibe_concentrate_ranking(ranking=ranking, db=db)
    submitted_ranking = await update_or_create_concentrate_ranking(ranking=ranking, db=db)
    return submitted_ranking


@router.get("/get_top_concentrate_strains", response_model=List[Dict[str, Any]])
async def get_top_concentrate_strains_route(db: Session = Depends(get_db)):
    avg_ratings = await return_average_concentrate_ratings(db)
    scored_strains = []
    for strain in avg_ratings:
        overall_score = sum(filter(None, strain[-7:])) / 7 if strain[-7:] else 0
        strain_data = {
            "strain": strain.strain,
            "cultivator": strain.cultivator,
            "flower_id": strain.concentrate_id,
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
    return return_strains


@router.get("/get_top_rated_concentrate_strains", response_model=list[Any])
async def get_top_rated_concentrate_strains_route(db: Session = Depends(get_db), top_n: int = 5):
    avg_ratings = await return_average_concentrate_ratings(db)
    scored_strains = []
    for strain in avg_ratings:
        overall_score = sum(filter(None, strain[-7:])) / 7 if strain[-7:] else 0
        strain_data = {
            "strain": strain.strain,
            "cultivator": strain.cultivator,
            "flower_id": strain.concentrate_id,
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
    return_strains = scored_strains[:top_n]
    for strain in return_strains:
        strain["url_path"] = return_image_url_from_supa_storage(str(Path(strain["url_path"])))
    return return_strains


@router.get(
    "/get_concentrate_ratings_by_id/{concentrate_id}",
    response_model=Union[ConcentrateRankingValuesSchema, RatingsErrorResponse],
)
async def get_concentrate_rankings_by_id_route(concentrate_id: int, db: Session = Depends(get_db)):
    ratings_dict = await get_concentrate_rankings_by_id(db, concentrate_id)
    return ratings_dict
