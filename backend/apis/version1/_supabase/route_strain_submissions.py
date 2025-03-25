#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb  4 10:16:42 2024

@author: dale
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from db.session import get_db
from db.repository.search_class import upsert_terp_profile
from schemas.product_types import ProductSubmission
from db.models import concentrates, edibles, flowers, pre_rolls
from core.config import settings


router = APIRouter()


@router.post("/submit_strain/", dependencies=[Depends(settings.jwt_auth_dependency)])
async def submit_strain(
    submission: ProductSubmission = Depends(ProductSubmission.as_form),
    db: Session = Depends(get_db),
):
    if submission.product_type == "flowerSubmission":
        model = flowers.Flower
    elif submission.product_type == "concentrateSubmission":
        model = concentrates.Concentrate
        card_path = "reviews/Connoisseur_Pack/CP_Rosin.webp"
    elif submission.product_type == "pre_rollSubmission":
        model = pre_rolls.Pre_Roll
    elif submission.product_type == "edibleSubmission":
        model = edibles.Edible
    else:
        raise HTTPException(status_code=400, detail="Invalid product type")
    existing_strain = (
        db.query(model)
        .filter(model.strain == submission.strain, model.cultivator == submission.cultivator)
        .first()
    )
    if existing_strain:
        new_submission = existing_strain
    if not card_path:
        card_path = "reviews/Connoisseur_Pack/CP_strains.webp"
    else:
        voting_open = True
        is_mystery = False
        new_submission = model(
            strain=submission.strain.strip(),
            cultivator=submission.cultivator.strip(),
            card_path=card_path,
            voting_open=voting_open,
            is_mystery=is_mystery,
        )
        try:
            db.add(new_submission)
        except Exception as e:
            print(f"Error: {e}\n\n")
            return None
        else:
            db.commit()
            db.refresh(new_submission)
    product_type_id = getattr(new_submission, f"{submission.product_type[:-10]}_id")
    product_description = await add_description_to_db(
        db,
        submission.product_type,
        product_type_id,
        submission.description,
        submission.effects,
        submission.cultivar_email,
        submission.lineage,
        submission.terpenes_list,
        submission.strain_category.value
    )
    await upsert_terp_profile(
        db,
        product_description.description_id,
        product_type_id,
        submission.product_type[:-10],
        submission.terpenes_map
    )
    return {
        "message": "Submission successful",
        "product_type_id": product_type_id,
        "submission_strain": new_submission.strain,
        "submission_cultivator": new_submission.cultivator,
        "cultivar_email": submission.cultivar_email,
    }


def parse_terpenes(terpenes_array: List[str]) -> list:
    terpenes_list = terpenes_array[0].split(",")
    processed_terpenes = []
    for terpene in terpenes_list:
        clean_terpene = terpene.replace("_", " ")
        clean_terpene = clean_terpene.replace("alpha", "α")
        clean_terpene = clean_terpene.replace("beta", "β")
        clean_terpene = clean_terpene.replace("gamma", "γ")
        clean_terpene = clean_terpene.replace("delta", "δ")
        processed_terpenes.append(clean_terpene.strip())
    return processed_terpenes


async def add_description_to_db(
    db: Session,
    product_type: str,
    product_id: int,
    description: str,
    effects: str,
    cultivar_email: str,
    lineage: str = "Coming Soon",
    terpenes_list: List[str] = ["Coming Soon"],
    strain_category: str = "cult_pack"
):
    description_model = None
    fk_column_name = None
    if product_type == "flowerSubmission":
        description_model = flowers.Flower_Description
        fk_column_name = "flower_id"
    elif product_type == "concentrateSubmission":
        description_model = concentrates.Concentrate_Description
        fk_column_name = "concentrate_id"
    elif product_type == "pre_rollSubmission":
        description_model = pre_rolls.Pre_Roll_Description
        fk_column_name = "pre_roll_id"
    elif product_type == "edibleSubmission":
        description_model = edibles.Edible_Description
        fk_column_name = "edible_id"
    if not description_model or not fk_column_name:
        raise ValueError(f"Invalid product_type: {product_type}")
    existing_description = (
        db.query(description_model)
        .filter(
            getattr(description_model, fk_column_name) == product_id,
            description_model.cultivar_email == cultivar_email
        )
        .first()
    )
    if existing_description:
        existing_description.description = description
        existing_description.effects = effects
        existing_description.lineage = lineage
        existing_description.terpenes_list = parse_terpenes(terpenes_list)
        existing_description.strain_category = strain_category
    else:
        # Create a new description
        fk_kwargs = {fk_column_name: product_id}
        new_description = description_model(
            **fk_kwargs,
            description=description,
            effects=effects,
            cultivar_email=cultivar_email,
            lineage=lineage,
            terpenes_list=parse_terpenes(terpenes_list),
            strain_category=strain_category
        )
        db.add(new_description)
    try:
        db.commit()
        db.refresh(existing_description if existing_description else new_description)
        return existing_description if existing_description else new_description
    except Exception as e:
        db.rollback()
        print(f"Error: {e}\n\n")
        return None
