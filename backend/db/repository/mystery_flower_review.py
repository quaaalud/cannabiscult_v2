#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 13 19:48:24 2023

@author: dale
"""

from sqlalchemy.orm import Session
from schemas.mystery_flower_review import CreateMysteryFlowerReview
from db.models.mystery_flower_review import MysteryFlowerReview


def create_mystery_flower_review(
        mystery_flower_review: CreateMysteryFlowerReview,
        db:Session):
    review_data_dict = mystery_flower_review.dict()
    created_mystery_review = MysteryFlowerReview(**review_data_dict)
    try:
        db.add(created_mystery_review)
    except:
        db.rollback()
    else:
        db.commit()
        db.refresh(created_mystery_review)
    finally:
        return created_mystery_review