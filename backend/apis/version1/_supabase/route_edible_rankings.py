#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 30 21:23:18 2023

@author: dale
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.session import get_db
from schemas.edible_rankings import CreateEdibleRanking, CreateVibeEdibleRanking
from db.repository.edible_rankings import create_edible_ranking, create_vibe_edible_ranking
from db.models.edible_rankings import Edible_Ranking, Vibe_Edible_Ranking


router = APIRouter()


@router.post("/submit-mystery-edible-ranking", response_model=None)
def submit_mystery_edible_ranking(
    edible_ranking: CreateEdibleRanking,
    db: Session = Depends(get_db)
) -> Edible_Ranking:
    submitted_ranking = create_edible_ranking(
        edible_ranking=edible_ranking,
        db=db
    )
    return submitted_ranking


@router.post("/submit-vibe-edible-ranking", response_model=None)
def submit_vibe_edible_ranking(
    edible_ranking: CreateVibeEdibleRanking,
    db: Session = Depends(get_db)
) -> Vibe_Edible_Ranking:
    submitted_ranking = create_vibe_edible_ranking(
        edible_ranking=edible_ranking,
        db=db
    )
    return submitted_ranking
