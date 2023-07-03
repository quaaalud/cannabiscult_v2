#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul  3 16:36:02 2023

@author: dale
"""

from fastapi import APIRouter
from sqlalchemy.orm import Session
from fastapi import Depends

from db.session import get_db
from schemas.flower_reviews import FlowerReviewUpdate, ShowFlowerReview
from db.repository.flower_reviews import get_review_data_and_path
from db.repository.flower_reviews import get_review_data_and_path_from_id
from db.repository.flower_reviews import append_votes_to_arrays
from db.models.flower_reviews import FlowerReview

router = APIRouter()


@router.get("/", response_model=ShowFlowerReview)
def get_flower_review(
    cultivator_select: str = None,
    strain_select: str = None,
    db: Session = Depends(get_db)) -> FlowerReview:
    review = get_review_data_and_path(
        cultivator_select,
        strain_select,
        db=db
    )
    return review


@router.get("/", response_model=ShowFlowerReview)
def get_flower_review_by_id(
    cultivator_select: str = None,
    strain_select: str = None,
    db: Session = Depends(get_db)) -> FlowerReview:
    review = get_review_data_and_path_from_id(
        cultivator_select,
        strain_select,
        db=db
    )
    return review


@router.post("/", response_model=FlowerReviewUpdate)
def post_cultivar_flower_review(
    review_id: int,
    structure_value: int,
    nose_value: int,
    flavor_value: int,
    effects_value: int,
    db: Session = Depends(get_db)) -> FlowerReview:
    review = append_votes_to_arrays(
        structure_value,
        nose_value,
        flavor_value,
        effects_value,
        db=db,
    )
    return review

