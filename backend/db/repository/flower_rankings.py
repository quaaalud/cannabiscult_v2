#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 30 21:10:27 2023

@author: dale
"""

from sqlalchemy.orm import Session
from schemas.flower_rankings import CreateHiddenFlowerRanking, CreateFlowerRanking
from db.models.flower_rankings import Hidden_Flower_Ranking, Flower_Ranking
from core.config import settings


@settings.retry_db
def create_flower_ranking(ranking_dict: CreateFlowerRanking, db: Session):
    ranking_data_dict = ranking_dict.dict()
    created_ranking = Flower_Ranking(**ranking_data_dict)
    try:
        db.add(created_ranking)
    except:
        db.rollback()
    else:
        db.commit()
        db.refresh(created_ranking)
    finally:
        return created_ranking

@settings.retry_db
def update_or_create_flower_ranking(ranking_dict: CreateFlowerRanking, db: Session):
    # Define the criteria for finding the existing record
    existing_ranking = (
        db.query(Flower_Ranking)
        .filter(
            Flower_Ranking.cultivator == ranking_dict.cultivator,
            Flower_Ranking.strain == ranking_dict.strain,
            Flower_Ranking.connoisseur == ranking_dict.connoisseur,
        )
        .first()
    )

    if existing_ranking:
        # Update existing record
        for key, value in ranking_dict.dict().items():
            setattr(existing_ranking, key, value)
        try:
            db.commit()
            db.refresh(existing_ranking)
            return existing_ranking
        except:
            db.rollback()
            raise
    else:
        # Create a new ranking record
        return create_flower_ranking(ranking_dict, db)

@settings.retry_db
def create_hidden_flower_ranking(ranking_dict: CreateHiddenFlowerRanking, db: Session):
    ranking_data_dict = ranking_dict.dict()
    created_ranking = Hidden_Flower_Ranking(**ranking_data_dict)
    try:
        db.add(created_ranking)
    except:
        db.rollback()
    else:
        db.commit()
        db.refresh(created_ranking)
    finally:
        return created_ranking
