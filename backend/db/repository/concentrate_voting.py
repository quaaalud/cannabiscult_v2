#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep  4 17:21:07 2023

@author: dale
"""

from sqlalchemy.orm import Session
from schemas.concentrate_voting import ConcentrateVoteCreate
from db.models.concentrate_voting import ConcentrateVoting
import datetime


def date_handler(obj):
    if isinstance(obj, datetime.date):
        return obj.isoformat()
    else:
        raise TypeError("Type %s not serializable" % type(obj))


def add_new_vote(concentrate_vote: ConcentrateVoteCreate, db: Session):
    vote = ConcentrateVoting(
        created_at=date_handler(datetime.datetime.now()),
        cultivator_selected=str(concentrate_vote.cultivator_selected),
        strain_selected=str(concentrate_vote.strain_selected),
        structure_vote=float(concentrate_vote.structure_vote),
        structure_explanation=str(concentrate_vote.structure_explanation),
        nose_vote=float(concentrate_vote.nose_vote),
        nose_explanation=str(concentrate_vote.nose_explanation),
        flavor_vote=float(concentrate_vote.flavor_vote),
        flavor_explanation=str(concentrate_vote.flavor_explanation),
        effects_vote=float(concentrate_vote.effects_vote),
        effects_explanation=str(concentrate_vote.effects_explanation),
        user_email=str(concentrate_vote.user_email),
    )
    try:
        db.add(vote)
    except:
        db.rollback()
    else:
        db.commit()
        db.refresh(vote)
    finally:
        return vote
