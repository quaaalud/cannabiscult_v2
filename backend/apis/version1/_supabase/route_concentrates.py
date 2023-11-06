#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep  4 17:26:25 2023

@author: dale
"""

from fastapi import APIRouter
from sqlalchemy.orm import Session
from fastapi import Depends, Query
from typing import List, Dict, Any
from db.session import get_supa_db, get_db
from db.repository.concentrate_reviews import append_votes_to_arrays
from db.repository.concentrate_reviews import get_review_data_and_path
from db.repository.concentrate_reviews import get_review_data_and_path_from_id
from db.repository.concentrates import get_concentrate_data_and_path
from db.models.concentrate_reviews import ConcentrateReview
from db.repository.concentrate_voting import add_new_vote
from schemas.concentrate_voting import ConcentrateVoteCreate


router = APIRouter()


def get_all_strains(
        db: Session = Depends(get_supa_db)) -> List[str]:
    all_strains = db.query(ConcentrateReview.strain).all()  
    return sorted(set([result[0] for result in all_strains]))
  
  
def get_all_strains_for_cultivator(
        cultivator_selected: str,
        db: Session = Depends(get_supa_db)) -> List[str]:
    all_strains = db.query(
        ConcentrateReview.strain
    ).filter(
        ConcentrateReview.cultivator == cultivator_selected
    ).all()  
    return sorted([result[0] for result in all_strains])
  
  
def get_all_cultivators(
        db: Session = Depends(get_supa_db)) -> List[str]:
    all_cultivators = db.query(ConcentrateReview.cultivator).all()  
    return sorted(set([result[0] for result in all_cultivators]))


def get_all_cultivators_for_strain(
        strain_selected: str,
        db: Session = Depends(get_supa_db)) -> List[str]:
    all_cultivators = db.query(
        ConcentrateReview.cultivator
    ).filter(
        ConcentrateReview.strain == strain_selected
    ).all()  
    return sorted(set([result[0] for result in all_cultivators]))


def return_selected_review(
        strain_selected: str,
        cultivator_selected: str,
        db: Session = Depends(get_supa_db)
        ):
    return get_review_data_and_path(
        db,
        cultivator_selected,
        strain_selected,
    )


def return_selected_review_by_id(
        selected_id: str,
        db: Session = Depends(get_supa_db)):
    return get_review_data_and_path_from_id(
        db,
        selected_id
    )


def add_new_votes_to_concentrate_values(
        cultivator_select: str,
        strain_select: str,
        structure_vote: int,
        nose_vote: int,
        flavor_vote: int,
        effects_vote: int,
        db: Session = Depends(get_supa_db)
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


@router.post("/")
def add_concentrate_vote_to_db(
        cultivator_selected: str,
        strain_selected: str,
        structure_vote: float,
        nose_vote: float,
        flavor_vote: float,
        effects_vote: float,
        user_email: str,
        structure_explanation: str = 'None',
        nose_explanation: str = 'None' ,
        flavor_explanation: str = 'None',
        effects_explanation: str = 'None',
        db: Session = Depends(get_supa_db)
    ):
    vote = ConcentrateVoteCreate(
        cultivator_selected = cultivator_selected,
        strain_selected = strain_selected,
        structure_vote = structure_vote,
        structure_explanation = structure_explanation,
        nose_vote = nose_vote,
        nose_explanation = nose_explanation,
        flavor_vote = flavor_vote,
        flavor_explanation = flavor_explanation,
        effects_vote = effects_vote,
        effects_explanation = effects_explanation,
        user_email = user_email,
    )
    return add_new_vote(
        vote,
        db=db,
    )


@router.get("/get-concentrate")
async def query_concentrate_by_strain(
    strain: str = Query(None, alias="strain"),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    return get_concentrate_data_and_path(
        db,
        strain_select=strain,
    )