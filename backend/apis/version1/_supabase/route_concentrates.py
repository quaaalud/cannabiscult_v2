#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep  4 17:26:25 2023

@author: dale
"""

from fastapi import APIRouter
from datetime import datetime, timedelta
from sqlalchemy import func
from sqlalchemy.orm import Session
from fastapi import Depends, Query, HTTPException
from typing import List, Dict, Any, Union
from db.session import get_db
from db.repository.concentrates import (
    get_concentrate_and_description,
    get_concentrate_data_and_path,
    get_vibe_concentrate_strains,
    get_concentrate_by_strain_and_cultivator,
    update_or_create_concentrate_ranking,
    create_vibe_concentrate_ranking,
    get_concentrate_rankings_by_id,
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


@router.post("/submit-concentrate-ranking", response_model=None)
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
async def get_top_concentrate_strains(db: Session = Depends(get_db)):
    avg_ratings = (
        db.query(
            Concentrate_Ranking.strain,
            Concentrate_Ranking.cultivator,
            func.avg(Concentrate_Ranking.color_rating),
            func.avg(Concentrate_Ranking.consistency_rating),
            func.avg(Concentrate_Ranking.smell_rating),
            func.avg(Concentrate_Ranking.flavor_rating),
            func.avg(Concentrate_Ranking.effects_rating),
            func.avg(Concentrate_Ranking.harshness_rating),
            func.avg(Concentrate_Ranking.residuals_rating),
        )
        .filter(Concentrate_Ranking.cultivator != "Cultivar")
        .filter(Concentrate_Ranking.strain.ilike("%Test%") == False)
        .group_by(Concentrate_Ranking.strain, Concentrate_Ranking.cultivator)
        .all()
    )
    scored_strains = []
    for strain in avg_ratings:
        overall_score = sum(filter(None, strain[2:])) / 7
        scored_strains.append((strain[0], strain[1], round(overall_score, 2)))
    scored_strains.sort(key=lambda x: x[2], reverse=True)
    top_strains = scored_strains[:3]
    return_strains = []
    for strain_dict in top_strains:
        try:
            concentrate_data = await get_concentrate_and_description(
                db, strain=strain_dict[0], cultivator=strain_dict[1]
            )
            concentrate_data["overall_score"] = strain_dict[2]
            return_strains.append(concentrate_data)
        except Exception:
            pass

    return return_strains


@router.get("/get_top_rated_concentrate_strains", response_model=list[Any])
async def get_top_rated_concentrate_strains(db: Session = Depends(get_db), top_n: int = 6):
    avg_ratings = (
        db.query(
            Concentrate_Ranking.strain,
            Concentrate_Ranking.cultivator,
            func.avg(Concentrate_Ranking.color_rating),
            func.avg(Concentrate_Ranking.consistency_rating),
            func.avg(Concentrate_Ranking.smell_rating),
            func.avg(Concentrate_Ranking.flavor_rating),
            func.avg(Concentrate_Ranking.effects_rating),
            func.avg(Concentrate_Ranking.harshness_rating),
            func.avg(Concentrate_Ranking.residuals_rating),
        )
        .filter(Concentrate_Ranking.date_posted >= (datetime.now() - timedelta(days=30)))
        .filter(Concentrate_Ranking.cultivator != "Cultivar")
        .filter(Concentrate_Ranking.strain.ilike("%Test%") == False)
        .group_by(Concentrate_Ranking.strain, Concentrate_Ranking.cultivator)
        .all()
    )
    scored_strains = []
    for strain in avg_ratings:
        overall_score = sum(filter(None, strain[2:])) / 7
        scored_strains.append((strain[0], strain[1], round(overall_score, 2)))
    top_strains = sorted(scored_strains, key=lambda x: x[2], reverse=True)[:top_n]
    return_strains = []
    for strain, cultivator, score in top_strains:
        try:
            concentrate_data = await get_concentrate_and_description(db, strain=strain, cultivator=cultivator)
            concentrate_data["overall_score"] = score
            for key, val in concentrate_data.items():
                try:
                    concentrate_data[key] = round(val, 2)
                except Exception:
                    pass
            return_strains.append(concentrate_data)
        except Exception:
            pass
    return return_strains


@router.get(
    "/get_concentrate_ratings_by_id/{concentrate_id}",
    response_model=Union[ConcentrateRankingValuesSchema, RatingsErrorResponse],
)
async def get_concentrate_ratings_by_id(concentrate_id: int, db: Session = Depends(get_db)):
    ratings_dict = await get_concentrate_rankings_by_id(db, concentrate_id)
    return ratings_dict
