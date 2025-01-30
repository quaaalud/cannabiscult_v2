#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep  4 17:26:25 2023

@author: dale
"""

from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import Dict, Any
from db.session import get_supa_db, get_db
from db.base import Flower_Ranking, FlowerReview, Hidden_Flower_Ranking, MysteryFlowerReview, FlowerVoting, Flower_Ranking
from db._supabase.connect_to_storage import get_image_from_results
from db._supabase.connect_to_storage import return_image_url_from_supa_storage
from schemas.flowers import (
    GetFlowerWithDescription,
    CreateHiddenFlowerRanking,
    FlowerVoteCreate,
    CreateFlowerRanking,
    CreateMysteryFlowerReview,
)
# New Flower Modules
from db.repository.flowers import (
    get_flower_and_description,
    get_flower_and_description_by_id,
    get_all_strains,
    get_all_strains_for_cultivator,
    get_all_cultivators,
    get_all_cultivators_for_strain,
    append_votes_to_arrays,
    get_review_data_and_path,
    get_review_data_and_path_from_id,
    get_flower_data_and_path,
    create_hidden_flower_ranking,
    update_or_create_flower_ranking,
    update_or_add_flower_vote,
    create_mystery_flower_review,
    add_new_votes_to_flower_values,
)


router = APIRouter()


@router.post("/vote/", response_model=Dict[str, Any])
def add_flower_vote_to_db(
    cultivator_selected: str,
    strain_selected: str,
    structure_vote: float,
    nose_vote: float,
    flavor_vote: float,
    effects_vote: float,
    user_email: str,
    structure_explanation: str = "None",
    nose_explanation: str = "None",
    flavor_explanation: str = "None",
    effects_explanation: str = "None",
    db: Session = Depends(get_supa_db),
):
    vote = FlowerVoteCreate(
        cultivator_selected=cultivator_selected,
        strain_selected=strain_selected,
        structure_vote=structure_vote,
        structure_explanation=structure_explanation,
        nose_vote=nose_vote,
        nose_explanation=nose_explanation,
        flavor_vote=flavor_vote,
        flavor_explanation=flavor_explanation,
        effects_vote=effects_vote,
        effects_explanation=effects_explanation,
        user_email=user_email,
    )
    return update_or_add_flower_vote(vote, db=db)


@router.get("/get-flower/", response_model=Dict[str, Any])
async def query_flower_by_strain(
    strain: str = Query(None, alias="strain"), db: Session = Depends(get_db)
) -> Dict[str, Any]:
    return get_flower_data_and_path(db, strain)


@router.get("/get_flower_description/", response_model=GetFlowerWithDescription)
async def query_flower_description_by_strain(
    strain: str = Query(None, alias="strain"),
    cultivator: str = Query(None, alias="cultivator"),
    cultivar_email: str = Query("aaron.childs@thesocialoutfitus.com", alias="cultivar"),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    flower_data = get_flower_and_description(db, strain, cultivar_email, cultivator)
    if flower_data:
        return flower_data
    else:
        raise HTTPException(status_code=404, detail="Flower or description not found")


@router.get("/get_flower_id/", response_model=GetFlowerWithDescription)
async def query_flower_with_description_by_id(
    flower_id: str = Query(None, alias="flower_id"),
    cultivar_email: str = Query("aaron.childs@thesocialoutfitus.com", alias="cultivar"),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    flower_data = get_flower_and_description_by_id(db, flower_id, cultivar_email)
    if flower_data:
        return flower_data
    else:
        raise HTTPException(status_code=404, detail="Flower or description not found")


@router.get("/get_flower_from_strain_and_cultivator", response_model=Dict[str, Any])
async def return_selected_review(strain_selected: str, cultivator_selected: str, db: Session = Depends(get_supa_db)):
    return get_review_data_and_path(db, cultivator_selected, strain_selected)


@router.post("/submit-hidden-flower-ranking", response_model=None)
def submit_mystery_flower_ranking(
    flower_ranking: CreateHiddenFlowerRanking, db: Session = Depends(get_db)
) -> Hidden_Flower_Ranking:
    submitted_ranking = create_hidden_flower_ranking(hidden_ranking=flower_ranking, db=db)
    return submitted_ranking


@router.post("/submit-flower-ranking", response_model=None)
def submit_flower_ranking(ranking: CreateFlowerRanking, db: Session = Depends(get_db)) -> Flower_Ranking:
    submitted_ranking = update_or_create_flower_ranking(ranking_dict=ranking, db=db)
    return submitted_ranking


@router.post("/submit-mystery-review", response_model=None)
def submit_mystery_flower_review(
    mystery_flower_review: CreateMysteryFlowerReview,
    db: Session = Depends(get_db)
) -> MysteryFlowerReview:
    submitted_review = create_mystery_flower_review(
        mystery_flower_review=mystery_flower_review,
        db=db
    )
    return submitted_review


@router.get("/get_top_flower_strains", response_model=list)
async def get_top_strains(db: Session = Depends(get_supa_db)):

    avg_ratings = (
        db.query(
            FlowerVoting.strain_selected,
            FlowerVoting.cultivator_selected,
            func.avg(FlowerVoting.structure_vote),
            func.avg(FlowerVoting.nose_vote),
            func.avg(FlowerVoting.flavor_vote),
            func.avg(FlowerVoting.effects_vote),
        )
        .filter(Flower_Ranking.cultivator != "Connoisseur")
        .filter(Flower_Ranking.strain.ilike("%Test%") == False)
        .group_by(FlowerVoting.strain_selected, FlowerVoting.cultivator_selected)
        .all()
    )
    scored_strains = []
    for strain in avg_ratings:
        overall_score = sum(filter(None, strain[2:])) / 4
        scored_strains.append((strain[0], strain[1], round(overall_score, 1)))
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
            flower_data["overall_score"] = strain_dict[2]
            return_strains.append(flower_data)
        except:
            pass

    return return_strains


@router.get("/get_top_rated_flower_strains", response_model=list)
async def get_top_flower_strains(db: Session = Depends(get_supa_db)):
    avg_ratings = (
        db.query(
            Flower_Ranking.strain,
            Flower_Ranking.cultivator,
            func.avg(Flower_Ranking.appearance_rating),
            func.avg(Flower_Ranking.smell_rating),
            func.avg(Flower_Ranking.flavor_rating),
            func.avg(Flower_Ranking.effects_rating),
            func.avg(Flower_Ranking.harshness_rating),
            func.avg(Flower_Ranking.freshness_rating),
        )
        .filter(Flower_Ranking.date_posted >= (datetime.now() - timedelta(days=30)))
        .filter(Flower_Ranking.cultivator != "Connoisseur")
        .filter(Flower_Ranking.strain.ilike("%Test%") == False)
        .group_by(Flower_Ranking.strain, Flower_Ranking.cultivator)
        .all()
    )
    scored_strains = []
    for strain in avg_ratings:
        overall_score = sum(filter(None, strain[2:])) / 6
        scored_strains.append((strain[0], strain[1], round(overall_score, 2)))
    scored_strains.sort(key=lambda x: x[2], reverse=True)
    top_strains = scored_strains[:5]

    return_strains = []
    for strain_dict in top_strains:
        flower_data = await get_flower_and_description(
            db,
            strain=strain_dict[0],
            cultivator=strain_dict[1],
            cultivar_email="aaron.childs@thesocialoutfitus.com",
        )
        flower_data["overall_score"] = strain_dict[2]

        return_strains.append(flower_data)

    return return_strains


@router.get("/get_strain_ratings_by_id/{flower_id}/", response_model=dict)
async def get_strain_ratings_by_id(flower_id: int, db: Session = Depends(get_supa_db)):
    # Query to calculate average ratings for a specific strain
    avg_ratings = (
        db.query(
            func.avg(Flower_Ranking.appearance_rating),
            func.avg(Flower_Ranking.smell_rating),
            func.avg(Flower_Ranking.flavor_rating),
            func.avg(Flower_Ranking.effects_rating),
            func.avg(Flower_Ranking.harshness_rating),
            func.avg(Flower_Ranking.freshness_rating),
        )
        .filter(Flower_Ranking.flower_id == flower_id)
        .first()
    )

    if not avg_ratings or any(rating is None for rating in avg_ratings):
        return {"error": "Flower not found or incomplete data"}

    overall_score = sum(avg_ratings) / 6

    flower_data = {
        "flower_id": flower_id,
        "overall_score": round(overall_score, 2),
        "appearance_rating": avg_ratings[0],
        "smell_rating": avg_ratings[1],
        "flavor_rating": avg_ratings[2],
        "effects_rating": avg_ratings[3],
        "harshness_rating": avg_ratings[4],
        "freshness_rating": avg_ratings[5],
    }

    return flower_data
