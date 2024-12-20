#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 30 21:23:18 2023

@author: dale
"""

from fastapi import APIRouter, Depends
from sqlalchemy import func
from typing import List, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from db.session import get_db
from db.models.concentrate_rankings import (
    Hidden_Concentrate_Ranking,
    Vibe_Concentrate_Ranking,
    Concentrate_Ranking,
)
from schemas.concentrate_rankings import (
    CreateHiddenConcentrateRanking,
    CreateConcentrateRanking,
)
from db.repository.concentrate_rankings import (
    update_or_create_concentrate,
    create_vibe_concentrate_ranking,
    create_concentrate_ranking,
)
from db.repository.concentrates import get_concentrate_and_description

router = APIRouter()


@router.post("/submit-concentrate-ranking", response_model=None)
async def submit_concentrate_ranking(
    concentrate_ranking: CreateConcentrateRanking, db: Session = Depends(get_db)
) -> Concentrate_Ranking:
    return await update_or_create_concentrate(ranking=concentrate_ranking, db=db)


@router.post("/submit-hidden-concentrate-ranking", response_model=None)
async def submit_mystery_concentrate_ranking(
    concentrate_ranking: CreateHiddenConcentrateRanking, db: Session = Depends(get_db)
) -> Hidden_Concentrate_Ranking:
    submitted_ranking = await update_or_create_concentrate(
        ranking=concentrate_ranking, db=db
    )
    return submitted_ranking


@router.post("/submit-vibe-concentrate-ranking", response_model=None)
async def submit_vibe_concentrate_ranking(
    ranking: CreateConcentrateRanking, db: Session = Depends(get_db)
) -> Vibe_Concentrate_Ranking:
    create_vibe_concentrate_ranking(ranking=ranking, db=db)
    submitted_ranking = await create_concentrate_ranking(ranking=ranking, db=db)
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
async def get_top_rated_concentrate_strains(
    db: Session = Depends(get_db), top_n: int = 5
):
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
            concentrate_data = await get_concentrate_and_description(
                db, strain=strain, cultivator=cultivator
            )
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
    "/get_concentrate_ratings_by_id/{concentrate_id}", response_model=Dict[str, Any]
)
async def get_concentrate_ratings_by_id(
    concentrate_id: int, db: Session = Depends(get_db)
):
    avg_ratings = (
        db.query(
            func.avg(Concentrate_Ranking.color_rating),
            func.avg(Concentrate_Ranking.consistency_rating),
            func.avg(Concentrate_Ranking.smell_rating),
            func.avg(Concentrate_Ranking.flavor_rating),
            func.avg(Concentrate_Ranking.effects_rating),
            func.avg(Concentrate_Ranking.harshness_rating),
            func.avg(Concentrate_Ranking.residuals_rating),
        )
        .filter(Concentrate_Ranking.concentrate_id == concentrate_id)
        .first()
    )

    if not avg_ratings or any(rating is None for rating in avg_ratings):
        return {"error": "Concentrate not found or incomplete data"}

    ratings_dict = {
        "concentrate_id": concentrate_id,
        "color_rating": round(avg_ratings[0], 2) if avg_ratings[0] is not None else None,
        "consistency_rating": (
            round(avg_ratings[1], 2) if avg_ratings[1] is not None else None
        ),
        "smell_rating": round(avg_ratings[2], 2) if avg_ratings[2] is not None else None,
        "flavor_rating": round(avg_ratings[3], 2) if avg_ratings[3] is not None else None,
        "effects_rating": (
            round(avg_ratings[4], 2) if avg_ratings[4] is not None else None
        ),
        "harshness_rating": (
            round(avg_ratings[5], 2) if avg_ratings[5] is not None else None
        ),
        "residuals_rating": (
            round(avg_ratings[6], 2) if avg_ratings[6] is not None else None
        ),
    }

    ratings_values = list(filter(None, avg_ratings))
    if ratings_values:

        overall_score = sum(ratings_values) / len(ratings_values)
        ratings_dict["overall_score"] = round(overall_score, 2)
    else:
        ratings_dict["overall_score"] = None

    return ratings_dict
