#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep  4 17:26:25 2023

@author: dale
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Union
from db.session import get_supa_db, get_db
from db.base import Flower_Ranking, Flower
from schemas.flowers import (
    FlowersBase,
    GetFlowerWithDescription,
    CreateFlowerRanking,
    FlowerReviewResponse,
    FlowerErrorResponse,
    GetFlowerRanking,
    FlowerRankingValuesSchema,
)
from db.repository.flowers import (
    get_flower_and_description,
    get_flower_and_description_by_id,
    get_review_data_and_path,
    get_flower_data_and_path,
    update_or_create_flower_ranking,
)

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
    avg_ratings = (
        db.query(
            Flower.strain,
            Flower.cultivator,
            Flower.flower_id,
            Flower_Ranking.flower_ranking_id,
            func.avg(Flower_Ranking.appearance_rating),
            func.avg(Flower_Ranking.smell_rating),
            func.avg(Flower_Ranking.flavor_rating),
            func.avg(Flower_Ranking.effects_rating),
            func.avg(Flower_Ranking.harshness_rating),
            func.avg(Flower_Ranking.freshness_rating),
        )
        .filter(
            Flower_Ranking.cultivator != "Connoisseur",
            Flower_Ranking.strain.ilike("%Test%") == False,
            Flower_Ranking.flower_ranking_id == Flower.flower_id,
        )
        .group_by(
            Flower.strain,
            Flower.cultivator,
        )
        .all()
    )
    scored_strains = []
    for strain in avg_ratings:
        overall_score = sum(filter(None, strain[4:])) / 6
        scored_strains.append((strain[0], strain[1], round(overall_score, 2)))
    scored_strains.sort(key=lambda x: x[2], reverse=True)
    top_strains = scored_strains[:3]
    return_strains = []
    for strain_dict in top_strains:
        try:
            flower_data = await get_flower_and_description(
                db,
                strain=strain_dict[0],
                cultivar_email="aaron.childs@thesocialoutfitus.com",
                cultivator=strain_dict[1],
            )
            if flower_data:
                flower_data["overall_score"] = strain_dict[2]
                return_strains.append(flower_data)
        except Exception as e:
            raise e
    return return_strains


@router.get("/get_top_rated_flower_strains", response_model=List)
async def get_top_flower_strains(db: Session = Depends(get_supa_db)):
    try:
        avg_ratings = (
            db.query(
                Flower_Ranking.strain,
                Flower_Ranking.cultivator,
                func.avg(Flower_Ranking.appearance_rating).label("appearance_rating"),
                func.avg(Flower_Ranking.smell_rating).label("smell_rating"),
                func.avg(Flower_Ranking.flavor_rating).label("flavor_rating"),
                func.avg(Flower_Ranking.effects_rating).label("effects_rating"),
                func.avg(Flower_Ranking.harshness_rating).label("harshness_rating"),
                func.avg(Flower_Ranking.freshness_rating).label("freshness_rating"),
            )
            .filter(
                Flower_Ranking.cultivator != "Connoisseur",
                ~Flower_Ranking.strain.ilike("%Test%"),
            )
            .group_by(
                Flower_Ranking.strain,
                Flower_Ranking.cultivator
            )
            .all()
        )
        scored_strains = []
        for strain in avg_ratings:
            ratings = [
                strain.appearance_rating,
                strain.smell_rating,
                strain.flavor_rating,
                strain.effects_rating,
                strain.harshness_rating,
                strain.freshness_rating,
            ]
            valid_ratings = [r for r in ratings if r is not None]
            overall_score = sum(valid_ratings) / len(valid_ratings) if valid_ratings else 0
            scored_strains.append((strain.strain, strain.cultivator, round(overall_score, 2)))
        scored_strains.sort(key=lambda x: x[2], reverse=True)
        top_strains = scored_strains[:6]
        return_strains = []
        for strain_dict in top_strains:
            flower_data = await get_flower_and_description(
                db,
                strain=strain_dict[0],
                cultivator=strain_dict[1],
                cultivar_email="aaron.childs@thesocialoutfitus.com",
            )
            if flower_data:
                flower_data["overall_score"] = strain_dict[2]
                return_strains.append(flower_data)
        return return_strains
    except Exception as e:
        raise e


@router.get(
    "/get_strain_ratings_by_id/{flower_id}/", response_model=Union[FlowerRankingValuesSchema, FlowerErrorResponse]
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
        return {"strain": "no match found", "error": "Flower not found or incomplete data for rankings."}
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
