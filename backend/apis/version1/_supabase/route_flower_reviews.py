#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul  3 16:36:02 2023

@author: dale
"""

from fastapi import APIRouter
from sqlalchemy.orm import Session
from fastapi import Depends
from typing import List
from db.session import get_supa_db
from db.repository.flower_reviews import append_votes_to_arrays
from db.repository.flower_reviews import get_review_data_and_path
from db.repository.flower_reviews import get_review_data_and_path_from_id
from db.models.flower_reviews import FlowerReview

router = APIRouter()


def get_all_strains(
        db: Session = Depends(get_supa_db)) -> List[str]:
    all_strains = db.query(FlowerReview.strain).all()  
    return [result[0] for result in all_strains]


def get_all_cultivators_for_strain(
        strain_selected: str,
        db: Session = Depends(get_supa_db)) -> List[str]:
    all_cultivators = db.query(
        FlowerReview.cultivator
    ).filter(
        FlowerReview.strain == strain_selected
    ).all()  
    return [result[0] for result in all_cultivators]


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


def add_new_votes_to_flower_strain(
        cultivator_select: str,
        strain_select: str,
        structure_value: int,
        nose_value: int,
        flavor_value: int,
        effects_value: int,
        db: Session = Depends(get_supa_db)
        ):
    return append_votes_to_arrays(
        cultivator_select,
        strain_select,
        structure_value,
        nose_value,
        flavor_value,
        effects_value,
        db,
    )