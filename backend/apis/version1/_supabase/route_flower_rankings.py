#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 30 21:23:18 2023

@author: dale
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.session import get_db
from db.models.flower_rankings import Hidden_Flower_Ranking, Flower_Ranking
from schemas.flower_rankings import CreateHiddenFlowerRanking, CreateFlowerRanking
from db.repository.flower_rankings import (
    create_hidden_flower_ranking,
    create_flower_ranking,
    update_or_create_flower_ranking,
)

router = APIRouter()


@router.post("/submit-hidden-flower-ranking", response_model=None)
def submit_mystery_flower_ranking(
    flower_ranking: CreateHiddenFlowerRanking, db: Session = Depends(get_db)
) -> Hidden_Flower_Ranking:
    submitted_ranking = create_hidden_flower_ranking(hidden_ranking=flower_ranking, db=db)
    return submitted_ranking


@router.post("/submit-flower-ranking", response_model=None)
def submit_flower_ranking(
    ranking: CreateFlowerRanking, db: Session = Depends(get_db)
) -> Flower_Ranking:
    submitted_ranking = update_or_create_flower_ranking(ranking_dict=ranking, db=db)
    return submitted_ranking
