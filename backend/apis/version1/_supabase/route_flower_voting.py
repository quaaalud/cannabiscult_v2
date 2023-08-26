#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Aug 20 22:09:10 2023

@author: dale
"""

from fastapi import APIRouter
from sqlalchemy.orm import Session
from fastapi import Depends
from db.session import get_supa_db
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
        structure_explanation: str = 'None',
        nose_explanation: str = 'None' ,
        flavor_explanation: str = 'None',
        effects_explanation: str = 'None',
        db: Session = Depends(get_supa_db)
    ):
    flower_vote = FlowerVoteCreate(
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
    return add_new_flower_vote(
        flower_vote,
        db=db,
    ) 