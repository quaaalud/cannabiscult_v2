#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep  4 17:06:46 2023

@author: dale
"""

import base64
from pathlib import Path
from sqlalchemy import func
from sqlalchemy.orm import Session
from db.models.concentrate_reviews import ConcentrateReview
from db._supabase.connect_to_storage import (
    get_image_from_results,
    return_image_url_from_supa_storage,
)


def get_review_data_and_path(
    db: Session, cultivator_select: str, strain_select: str
) -> ConcentrateReview:
    review = (
        db.query(ConcentrateReview)
        .filter(
            (ConcentrateReview.cultivator == cultivator_select)
            & (ConcentrateReview.strain == strain_select)
        )
        .first()
    )
    if review:
        img_path = str(Path(review.card_path))
        results_bytes = return_image_url_from_supa_storage(img_path)
        struct_avg = get_average_of_list(review.structure)
        nose_avg = get_average_of_list(review.nose)
        flavor_avg = get_average_of_list(review.flavor)
        effects_avg = get_average_of_list(review.effects)
        total_avg = get_average_of_list([struct_avg, nose_avg, flavor_avg, effects_avg])
        return {
            "id": review.id,
            "strain": review.strain,
            "cultivator": review.cultivator,
            "overall": total_avg,
            "structure": struct_avg,
            "nose": nose_avg,
            "flavor": flavor_avg,
            "effects": effects_avg,
            "vote_count": review.vote_count,
            "url_path": results_bytes,
            "terpene_list": review.terpene_list,
        }
    else:
        return {"strain": strain_select, "message": "Review not found"}


def get_average_of_list(_list_of_floats: list[float]) -> float:
    return round(sum(_list_of_floats) / len(_list_of_floats) * 2) / 2


def get_review_data_and_path_from_id(db: Session, id_selected: int) -> ConcentrateReview:

    review = db.query(ConcentrateReview).filter(ConcentrateReview.id == id_selected).first()

    if review:
        results_bytes = return_image_url_from_supa_storage(str(Path(review.card_path)))
        return {
            "id": review.id,
            "strain": review.strain,
            "cultivator": review.cultivator,
            "overall": review.overall,
            "structure": get_average_of_list(review.structure),
            "nose": get_average_of_list(review.nose),
            "flavor": get_average_of_list(review.flavor),
            "effects": get_average_of_list(review.effects),
            "vote_count": review.vote_count,
            "url_path": results_bytes,
        }
    else:
        return {"review_id": id_selected, "message": "Review not found"}


def append_votes_to_arrays(
    cultivator_select: str,
    strain_select: str,
    structure_value: int,
    nose_value: int,
    flavor_value: int,
    effects_value: int,
    db: Session,
):

    review = (
        db.query(ConcentrateReview)
        .filter(
            (ConcentrateReview.strain == strain_select)
            & (ConcentrateReview.cultivator == cultivator_select)
        )
        .first()
    )

    if review:
        review.structure = func.array_append(ConcentrateReview.structure, structure_value)
        review.nose = func.array_append(ConcentrateReview.nose, nose_value)
        review.flavor = func.array_append(ConcentrateReview.flavor, flavor_value)
        review.effects = func.array_append(ConcentrateReview.effects, effects_value)
        review.vote_count = ConcentrateReview.vote_count + 1
        try:
            db.flush()
            db.commit()
            db.refresh(review)
            results_bytes = get_image_from_results(str(Path(review.card_path)))
            return {
                "id": review.id,
                "strain": review.strain,
                "cultivator": review.cultivator,
                "overall": review.overall,
                "structure": get_average_of_list(review.structure),
                "nose": get_average_of_list(review.nose),
                "flavor": get_average_of_list(review.flavor),
                "effects": get_average_of_list(review.effects),
                "vote_count": review.vote_count,
                "card_path": results_bytes,
            }
        except Exception as e:
            db.rollback()
            print(f"Error: {e}")
            return {"strain": strain_select, "message": "Failed to append values"}
    else:
        return {"strain": strain_select, "message": "Review not found"}


def calculate_overall_score(
    structure_val: float,
    nose_val: float,
    flavor_val: float,
    effects_val: float,
):
    values_list = [structure_val, nose_val, flavor_val, effects_val]
    return get_average_of_list(values_list)


def convert_img_bytes_for_html(img_bytes):
    return base64.b64encode(img_bytes).decode()
