#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb  4 10:16:42 2024

@author: dale
"""

from fastapi import APIRouter, Form, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from db.session import get_db
from db.models import concentrates, edibles, flowers, pre_rolls


router = APIRouter()


@router.post("/submit_strain/")
async def submit_strain(
    background_tasks: BackgroundTasks,
    product_type: str = Form(...),
    strain: str = Form(...),
    cultivator: str = Form(...),
    cultivar_email: str = Form(...),
    description: str = Form("Coming Soon!"),
    effects: str = Form("Coming Soon!"),
    lineage: str = Form("Coming Soon!"),
    terpenes_list: List[str] = Form(["Coming", "Soon!"]),
    db: Session = Depends(get_db),
):
    # Determine the table/model to use based on product_type
    model = None
    if product_type == "flowerSubmission":
        model = flowers.Flower
    elif product_type == "concentrateSubmission":
        model = concentrates.Concentrate
    elif product_type == "pre_rollSubmission":
        model = pre_rolls.Pre_Roll
    elif product_type == "edibleSubmission":
        model = edibles.Edible
    else:
        raise HTTPException(status_code=400, detail="Invalid product type")

    existing_strain = (
        db.query(model)
        .filter(model.strain == strain.title(), model.cultivator == cultivator.title())
        .first()
    )
    if existing_strain:
        new_submission = existing_strain
    else:
        card_path = "reviews/Connoisseur_Pack/CP_strains.png"
        voting_open = True
        is_mystery = False

        # Create a new instance of the model with the form data
        new_submission = model(
            strain=strain.title(),
            cultivator=cultivator.title(),
            card_path=card_path,
            voting_open=voting_open,
            is_mystery=is_mystery,
        )

        # Add the new submission to the database
        try:
            db.add(new_submission)
        except Exception as e:
            print(f"Error: {e}\n\n")
            return None
        else:
            db.commit()
            db.refresh(new_submission)

    product_type_id = getattr(new_submission, f"{product_type[:-10]}_id")

    background_tasks.add_task(
        add_description_to_db,
        db,
        product_type,
        product_type_id,
        description,
        effects,
        cultivar_email,
        lineage,
        terpenes_list,
    )

    return {
        "message": "Submission successful",
        "product_type_id": product_type_id,
        "submission_strain": new_submission.strain,
        "submission_cultivator": new_submission.cultivator,
        "cultivar_email": cultivar_email,
    }


def parse_terpenes(terpenes_array: List[str]) -> list:
    # Split the string on commas to create a list
    terpenes_list = terpenes_array[0].split(",")

    # Replace underscores with spaces and specific substrings with symbols
    processed_terpenes = []
    for terpene in terpenes_list:
        # Replace underscores with spaces
        clean_terpene = terpene.replace("_", " ")

        # Replace specific substrings with Greek symbols
        clean_terpene = clean_terpene.replace("alpha", "α")
        clean_terpene = clean_terpene.replace("beta", "β")
        clean_terpene = clean_terpene.replace("gamma", "γ")
        clean_terpene = clean_terpene.replace("delta", "δ")

        # Add the processed terpene to the list
        processed_terpenes.append(clean_terpene.strip())

    return processed_terpenes


def add_description_to_db(
    db: Session,
    product_type: str,
    product_id: int,
    description: str,
    effects: str,
    cultivar_email: str,
    lineage: str = "Coming Soon",
    terpenes_list: List[str] = ["Coming Soon"],
):
    description_model = None
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
    fk_kwargs = {fk_column_name: product_id}
    new_description = description_model(
        **fk_kwargs,
        description=description,
        effects=effects,
        cultivar_email=cultivar_email,
        lineage=lineage,
        terpenes_list=parse_terpenes(terpenes_list),
    )
    try:
        db.add(new_description)
    except Exception as e:
        print(f"Error: {e}\n\n")
        return None
    else:
        db.commit()
        db.refresh(new_description)
    return new_description
