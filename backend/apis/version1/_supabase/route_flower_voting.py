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
from db.session import get_supa_db
from db.models.flower_voting import FlowerVoting
from db.repository.flower_voting import add_new_flower_vote
from schemas.flower_voting import FlowerVoteCreate


router = APIRouter()


@router.post("/")
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
        .group_by(FlowerVoting.strain_selected, FlowerVoting.cultivator_selected)
        .all()
    )
    scored_strains = []
    for strain in avg_ratings:
        overall_score = (
            sum(filter(None, strain[2:])) / 4
        )
        scored_strains.append((strain[0], strain[1], round(overall_score, 1)))
    scored_strains.sort(key=lambda x: x[2], reverse=True)
    top_strains = scored_strains[:3]

    return top_strains
