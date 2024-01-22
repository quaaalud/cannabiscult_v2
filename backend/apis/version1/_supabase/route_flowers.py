#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep  4 17:26:25 2023

@author: dale
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from db.session import get_supa_db, get_db
from db.repository.flower_reviews import append_votes_to_arrays
from db.repository.flower_reviews import get_review_data_and_path
from db.repository.flower_reviews import get_review_data_and_path_from_id
from db.repository.flowers import get_flower_data_and_path
from db.models.flower_reviews import FlowerReview
from db.repository.flower_voting import add_new_flower_vote
from schemas.flower_rankings import FlowerVoteCreate

# New Flower Modules
from db.repository.flowers import get_flower_and_description, get_flower_and_description_by_id


router = APIRouter()


def get_all_strains(db: Session = Depends(get_supa_db)) -> List[str]:
    all_strains = db.query(FlowerReview.strain).all()
    return sorted(set([result[0] for result in all_strains]))


def get_all_strains_for_cultivator(
    cultivator_selected: str, db: Session = Depends(get_supa_db)
) -> List[str]:
    all_strains = (
        db.query(FlowerReview.strain).filter(FlowerReview.cultivator == cultivator_selected).all()
    )
    return sorted([result[0] for result in all_strains])


def get_all_cultivators(db: Session = Depends(get_supa_db)) -> List[str]:
    all_cultivators = db.query(FlowerReview.cultivator).all()
    return sorted(set([result[0] for result in all_cultivators]))


def get_all_cultivators_for_strain(
    strain_selected: str, db: Session = Depends(get_supa_db)
) -> List[str]:
    all_cultivators = (
        db.query(FlowerReview.cultivator).filter(FlowerReview.strain == strain_selected).all()
    )
    return sorted(set([result[0] for result in all_cultivators]))


def return_selected_review(
    strain_selected: str, cultivator_selected: str, db: Session = Depends(get_supa_db)
):
    return get_review_data_and_path(
        db,
        cultivator_selected,
        strain_selected,
    )


def return_selected_review_by_id(selected_id: str, db: Session = Depends(get_supa_db)):
    return get_review_data_and_path_from_id(db, selected_id)


def add_new_votes_to_flower_values(
    cultivator_select: str,
    strain_select: str,
    structure_vote: int,
    nose_vote: int,
    flavor_vote: int,
    effects_vote: int,
    db: Session = Depends(get_supa_db),
):
    try:
        return append_votes_to_arrays(
            cultivator_select,
            strain_select,
            structure_vote,
            nose_vote,
            flavor_vote,
            effects_vote,
            db,
        )
    except:
        pass


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
    return add_new_flower_vote(
        vote,
        db=db,
    )


@router.get("/get-flower", response_model=Dict[str, Any])
async def query_flower_by_strain(
    strain: str = Query(None, alias="strain"), db: Session = Depends(get_db)
) -> Dict[str, Any]:
    return get_flower_data_and_path(
        db,
        strain,
    )


@router.get("/get_flower_description", response_model=Dict[str, Any])
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


@router.get("/get_flower_id", response_model=Dict[str, Any])
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
