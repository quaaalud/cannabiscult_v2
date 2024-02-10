#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb  4 10:16:42 2024

@author: dale
"""

from fastapi import APIRouter, Form, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session
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

    card_path = "reviews/Connoisseur_Pack/CP_strains.png"
    voting_open = True
    is_mystery = False

    # Create a new instance of the model with the form data
    new_submission = model(
        strain=strain,
        cultivator=cultivator,
        card_path=card_path,
        voting_open=voting_open,
        is_mystery=is_mystery,
    )

    # Add the new submission to the database
    db.add(new_submission)
    db.commit()
    db.refresh(new_submission)

    id_column_name = f"{product_type[:-10]}_id"  # Removes 'Submission' from the end and adds '_id'
    product_type_id = getattr(new_submission, id_column_name)

    background_tasks.add_task(
        add_description_to_db,
        product_type,
        product_type_id,
        description,
        effects,
        cultivar_email,
        db,
    )

    return {
        "message": "Submission successful",
        "product_type_id": product_type_id,
        "submission_strain": new_submission.strain,
        "submission_cultivator": new_submission.cultivator,
        "cultivar_email": cultivar_email,
    }


def add_description_to_db(
    product_type: str,
    product_id: int,
    description: str,
    effects: str,
    cultivar_email: str,
    db: Session,
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
    )

    db.add(new_description)
    db.commit()
