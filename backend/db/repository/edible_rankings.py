#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 30 21:10:27 2023

@author: dale
"""

from sqlalchemy.orm import Session
from schemas.edible_rankings import CreateMysteryEdibleRanking
from db.models.edible_rankings import MysteryEdibleRanking
from schemas.edible_rankings import CreateVividEdibleRanking
from db.models.edible_rankings import Vivid_Edible_Ranking
from schemas.edible_rankings import CreateVibeEdibleRanking
from db.models.edible_rankings import Vibe_Edible_Ranking


def create_mystery_edible_ranking(
        edible_ranking: CreateMysteryEdibleRanking,
        db:Session):
    ranking_data_dict = edible_ranking.dict()
    created_edible_ranking = MysteryEdibleRanking(**ranking_data_dict)
    try:
        db.add(created_edible_ranking)
    except:
        db.rollback()
    else:
        db.commit()
        db.refresh(created_edible_ranking)
    finally:
        return created_edible_ranking
      
      
def create_vivid_edible_ranking(
        edible_ranking: CreateVividEdibleRanking,
        db:Session):
    ranking_data_dict = edible_ranking.dict()
    created_edible_ranking = Vivid_Edible_Ranking(**ranking_data_dict)
    try:
        db.add(created_edible_ranking)
    except:
        db.rollback()
    else:
        db.commit()
        db.refresh(created_edible_ranking)
    finally:
        return created_edible_ranking
      
      
def create_vibe_edible_ranking(
        edible_ranking: CreateVibeEdibleRanking,
        db:Session):
    ranking_data_dict = edible_ranking.dict()
    created_edible_ranking = Vibe_Edible_Ranking(**ranking_data_dict)
    try:
        db.add(created_edible_ranking)
    except:
        db.rollback()
    else:
        db.commit()
        db.refresh(created_edible_ranking)
    finally:
        return created_edible_ranking