#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jul  2 23:18:56 2023

@author: dale
"""

import base64
from pathlib import Path
from sqlalchemy.orm import Session
from db.models.flower_reviews import FlowerReview
from db._supabase.connect_to_storage import get_image_from_results 

def get_review_data_and_path(
        db: Session,
        cultivator_select: str,
        strain_select: str) -> FlowerReview:
    review = db.query(
        FlowerReview
    ).filter(
        (FlowerReview.cultivator == cultivator_select) &
        (FlowerReview.strain == strain_select)
    ).first()
    if review:
        results_bytes = get_image_from_results(
            str(Path(review.card_path))
        )
        return {
            'id': review.id,
            'strain': review.strain,
            'cultivator': review.cultivator,
            'overall': review.overall,
            'structure': review.structure,
            'nose': review.nose,
            'flavor': review.flavor,
            'effects': review.effects,
            'vote_count': review.vote_count,
            'card_path': results_bytes,
        }
    else:
        return {
            'strain': strain_select,
            'message': 'Review not found'
        }


def get_review_data_and_path_from_id(
        db: Session,
        id_selected: int) -> FlowerReview:

    review = db.query(
        FlowerReview
    ).filter(
        FlowerReview.id == id_selected
    ).first()
        
    if review:
        results_bytes = get_image_from_results(
            str(Path(review.card_path))
        )
        return {
            'id': review.id,
            'strain': review.strain,
            'cultivator': review.cultivator,
            'overall': review.overall,
            'structure': review.structure,
            'nose': review.nose,
            'flavor': review.flavor,
            'effects': review.effects,
            'vote_count': review.vote_count,
            'card_path': results_bytes,
        }
    else:
        return {
            'review_id': id_selected,
            'message': 'Review not found'
        }


def append_votes_to_arrays(
        cultivator_select: str,
        strain_select: str,
        structure_value: int,
        nose_value: int,
        flavor_value: int,
        effects_value: int,
        db: Session):

    review = db.query(
        FlowerReview
    ).filter(
        (FlowerReview.strain == strain_select) &
        (FlowerReview.cultivator == cultivator_select)
    ).first()

    if review:
        review.structure.append(structure_value)
        review.nose.append(nose_value)
        review.flavor.append(flavor_value)
        review.effects.append(effects_value)
        try:
            db.commit()
            db.refresh(review)
            results_bytes = get_image_from_results(
                str(Path(review.card_path))
            )
            return {
                'id': review.id,
                'strain': review.strain,
                'cultivator': review.cultivator,
                'overall': review.overall,
                'structure': review.structure,
                'nose': review.nose,
                'flavor': review.flavor,
                'effects': review.effects,
                'vote_count': review.vote_count,
                'card_path': results_bytes,
            }
        except:
            db.rollback()
            return {
                "strain": strain_select,
                "message": "Failed to append values"
            }
    else:
        return {
            "strain": strain_select,
            "message": "Review not found"
        }


def convert_img_bytes_for_html(img_bytes):
    return base64.b64encode(img_bytes).decode()
        