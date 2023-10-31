#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 30 22:14:44 2023

@author: dale
"""

from fastapi import APIRouter
from sqlalchemy.orm import Session
from fastapi import Depends
from db.session import get_supa_db
from db.repository.mystery_edibles import get_edible_data_and_path
from db.models.mystery_edibles import MysteryEdible

router = APIRouter()


def get_all_mystery_edibles(
        db: Session = Depends(get_supa_db)) -> MysteryEdible:
    all_strains = db.query(MysteryEdible.strain).all()
    return sorted(set([result[0] for result in all_strains]))


def return_selected_mystery_edible(
        strain_selected: str,
        db: Session = Depends(get_supa_db)
) -> MysteryEdible:
    return get_edible_data_and_path(
        db,
        strain_select=strain_selected,
    )
