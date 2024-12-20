#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Aug 20 22:09:10 2023

@author: dale
"""

from fastapi import APIRouter
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import Depends
from typing import Dict, Any
from datetime import datetime, timedelta
from db.session import get_supa_db
from db.models.flower_voting import FlowerVoting
from db.models.flower_rankings import Flower_Ranking
from db.repository.flower_voting import add_new_flower_vote
from schemas.flower_rankings import FlowerVoteCreate

# New Flower Models
from db.repository.flowers import get_flower_and_description

router = APIRouter()


@router.post("/", response_model=Dict[str, Any])
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
    flower_vote = FlowerVoteCreate(
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
    return add_new_flower_vote(
        flower_vote,
        db=db,
    )


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


@router.get("/get_strain_ratings_by_id/{flower_id}", response_model=dict)
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
