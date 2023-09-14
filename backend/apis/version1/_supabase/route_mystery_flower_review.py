#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 13 19:57:15 2023

@author: dale
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.session import get_db
from schemas.mystery_flower_review import CreateMysteryFlowerReview
from db.repository.mystery_flower_review import create_mystery_flower_review
from db.models.mystery_flower_review import MysteryFlowerReview


router = APIRouter()


@router.post("/", response_model=None)
def submit_mystery_flower_review(
    mystery_flower_review: CreateMysteryFlowerReview,
    db: Session = Depends(get_db)
) -> MysteryFlowerReview:
    mystery_flower_review = create_mystery_flower_review(
        voter=mystery_flower_review,
        db=db
    )
    return mystery_flower_review
