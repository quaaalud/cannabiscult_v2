#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 30 21:10:27 2023

@author: dale
"""

from sqlalchemy.orm import Session
from schemas.concentrate_rankings import CreateHiddenConcentrateRanking
from db.models.concentrate_rankings import Hidden_Concentrate_Ranking


def create_hidden_concentrate_ranking(
        hidden_ranking: CreateHiddenConcentrateRanking,
        db:Session):
    ranking_data_dict = hidden_ranking.dict()
    created_ranking = Hidden_Concentrate_Ranking(**ranking_data_dict)
    try:
        db.add(created_ranking)
    except:
        db.rollback()
    else:
        db.commit()
        db.refresh(created_ranking)
    finally:
        return created_ranking
      