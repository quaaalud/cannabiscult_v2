#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 30 21:23:18 2023

@author: dale
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.session import get_db
from db.models.concentrate_rankings import Hidden_Concentrate_Ranking, Vibe_Concentrate_Ranking
from schemas.concentrate_rankings import CreateHiddenConcentrateRanking, CreateConcentrateRanking
from db.repository.concentrate_rankings import (
    create_hidden_concentrate_ranking,
    create_vibe_concentrate_ranking,
)

router = APIRouter()


@router.post("/submit-hidden-concentrate-ranking", response_model=None)
def submit_mystery_concentrate_ranking(
    concentrate_ranking: CreateHiddenConcentrateRanking, db: Session = Depends(get_db)
) -> Hidden_Concentrate_Ranking:
    submitted_ranking = create_hidden_concentrate_ranking(hidden_ranking=concentrate_ranking, db=db)
    return submitted_ranking


@router.post("/submit-vibe-concentrate-ranking", response_model=None)
def submit_vibe_concentrate_ranking(
    ranking: CreateConcentrateRanking, db: Session = Depends(get_db)
) -> Vibe_Concentrate_Ranking:
    submitted_ranking = create_vibe_concentrate_ranking(ranking=ranking, db=db)
    return submitted_ranking
