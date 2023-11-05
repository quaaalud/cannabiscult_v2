#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 30 21:23:18 2023

@author: dale
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.session import get_db
from schemas.edible_rankings import CreateMysteryEdibleRanking
from db.repository.edible_rankings import create_mystery_edible_ranking
from db.models.edible_rankings import MysteryEdibleRanking
from schemas.edible_rankings import CreateVividEdibleRanking
from db.repository.edible_rankings import create_vivid_edible_ranking
from db.models.edible_rankings import Vivid_Edible_Ranking
from schemas.edible_rankings import CreateVibeEdibleRanking
from db.repository.edible_rankings import create_vibe_edible_ranking
from db.models.edible_rankings import Vibe_Edible_Ranking


router = APIRouter()


@router.post("/submit-mystery-edible-ranking", response_model=None)
def submit_mystery_edible_ranking(
    mystery_edible_ranking: CreateMysteryEdibleRanking,
    db: Session = Depends(get_db)
) -> MysteryEdibleRanking:
    submitted_ranking = create_mystery_edible_ranking(
        mystery_edible_ranking=mystery_edible_ranking,
        db=db
    )
    return submitted_ranking
  
  
@router.post("/submit-vivid-edible-ranking", response_model=None)
def submit_vivid_edible_ranking(
    edible_ranking: CreateVividEdibleRanking,
    db: Session = Depends(get_db)
) -> Vivid_Edible_Ranking:
    submitted_ranking = create_vivid_edible_ranking(
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