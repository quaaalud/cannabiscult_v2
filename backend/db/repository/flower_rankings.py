#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 30 21:10:27 2023

@author: dale
"""

from sqlalchemy.orm import Session
from schemas.flower_rankings import CreateHiddenFlowerRanking, CreateFlowerRanking
from db.models.flower_rankings import Hidden_Flower_Ranking, Flower_Ranking


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
