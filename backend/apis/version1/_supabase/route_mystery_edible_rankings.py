#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 30 21:23:18 2023

@author: dale
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.session import get_db
from schemas.mystery_edible_rankings import CreateMysteryEdibleRanking
from db.repository.mystery_edible_rankings import create_mystery_edible_ranking
from db.models.mystery_flower_review import MysteryFlowerReview


router = APIRouter()


@router.post("/submit-mystery-edible-ranking", response_model=None)
def submit_mystery_edible_ranking(
    mystery_edible_ranking: CreateMysteryEdibleRanking,
    db: Session = Depends(get_db)
) -> MysteryFlowerReview:
    submitted_ranking = create_mystery_edible_ranking(
        mystery_edible_ranking=mystery_edible_ranking,
        db=db
    )
    return submitted_ranking