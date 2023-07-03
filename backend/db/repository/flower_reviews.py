#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jul  2 23:18:56 2023

@author: dale
"""

from sqlalchemy.orm import Session
from db.models.flower_reviews import FlowerReview


def get_review_data_and_path(
        db: Session,
        cultivator_select: str=None,
        strain_select: str=None) -> FlowerReview:
    if cultivator_select and strain_select:
        review = db.query(
            FlowerReview
        ).filter(
            (FlowerReview.cultivator == cultivator_select) &
            (FlowerReview.strain == strain_select)
        ).first()
        if review:
            return {
                'review_obj': review
            }
        else:
            return {
                'strain': strain_select,
                'message': 'Review not found'
            }


def append_to_arrays(
        review_id: int,
        structure_value: int,
        nose_value: int,
        flavor_value: int,
        effects_value: int,
        db: Session):
    
    review = db.query(
        FlowerReview
    ).filter(
        FlowerReview.id == review_id
    ).first()

    if review:
        review.structure.append(structure_value)
        review.nose.append(nose_value)
        review.flavor.append(flavor_value)
        review.effects.append(effects_value)
        try:
            db.commit()
            db.refresh(review)
            return review
        except:
            db.rollback()
            return {
                "review_id": review_id, 
                "message": "Failed to append values"
            }
    else:
        return {
            "review_id": review_id, 
            "message": "Review not found"
        }