#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 30 21:10:27 2023

@author: dale
"""

from sqlalchemy.orm import Session
from schemas.mystery_edible_rankings import CreateMysteryEdibleRanking
from db.models.mystery_edible_rankings import MysteryEdibleRanking


def create_mystery_edible_ranking(
        mystery_edible_ranking: CreateMysteryEdibleRanking,
        db:Session):
    ranking_data_dict = mystery_edible_ranking.dict()
    created_mystery_ranking = MysteryEdibleRanking(**ranking_data_dict)
    try:
        db.add(created_mystery_ranking)
    except:
        db.rollback()
    else:
        db.commit()
        db.refresh(created_mystery_ranking)
    finally:
        return created_mystery_ranking