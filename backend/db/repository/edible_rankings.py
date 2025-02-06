#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 30 21:10:27 2023

@author: dale
"""

from sqlalchemy.orm import Session
from db.models.edible_rankings import Edible_Ranking, Vibe_Edible_Ranking
from schemas.edible_rankings import CreateEdibleRanking, CreateVibeEdibleRanking
from core.config import settings


@settings.retry_db
def create_edible_ranking(edible_ranking: CreateEdibleRanking, db: Session):
    ranking_data_dict = edible_ranking.dict()
    created_edible_ranking = Edible_Ranking(**ranking_data_dict)
    try:
        db.add(created_edible_ranking)
    except Exception:
        db.rollback()
    else:
        db.commit()
        db.refresh(created_edible_ranking)
    finally:
        return created_edible_ranking


@settings.retry_db
def create_vibe_edible_ranking(edible_ranking: CreateVibeEdibleRanking, db: Session):
    ranking_data_dict = edible_ranking.dict()
    created_edible_ranking = Vibe_Edible_Ranking(**ranking_data_dict)
    try:
        db.add(created_edible_ranking)
    except Exception:
        db.rollback()
    else:
        db.commit()
        db.refresh(created_edible_ranking)
    finally:
        return created_edible_ranking
