#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Aug 20 21:57:10 2023

@author: dale
"""

from sqlalchemy.orm import Session
from schemas.flower_rankings import FlowerVoteCreate
from db.models.flower_voting import FlowerVoting
import datetime


def date_handler(obj):
    if isinstance(obj, datetime.date):
        return obj.isoformat()
    else:
        raise TypeError("Type %s not serializable" % type(obj))


def add_new_flower_vote(flower_vote: FlowerVoteCreate, db: Session):
    flower_vote = FlowerVoting(
        created_at=date_handler(datetime.datetime.now()),
        cultivator_selected=str(flower_vote.cultivator_selected),
        strain_selected=str(flower_vote.strain_selected),
        structure_vote=float(flower_vote.structure_vote),
        structure_explanation=str(flower_vote.structure_explanation),
        nose_vote=float(flower_vote.nose_vote),
        nose_explanation=str(flower_vote.nose_explanation),
        flavor_vote=float(flower_vote.flavor_vote),
        flavor_explanation=str(flower_vote.flavor_explanation),
        effects_vote=float(flower_vote.effects_vote),
        effects_explanation=str(flower_vote.effects_explanation),
        user_email=str(flower_vote.user_email),
    )
    try:
        db.add(flower_vote)
    except:
        db.rollback()
    else:
        db.commit()
        db.refresh(flower_vote)
    finally:
        return flower_vote


def update_or_add_flower_vote(flower_vote: FlowerVoteCreate, db: Session):
    existing_vote = (
        db.query(FlowerVoting)
        .filter(
            FlowerVoting.cultivator_selected == flower_vote.cultivator_selected,
            FlowerVoting.strain_selected == flower_vote.strain_selected,
            FlowerVoting.user_email == flower_vote.user_email,
        )
        .first()
    )

    if existing_vote:
        # Update existing record
        existing_vote.structure_vote = float(flower_vote.structure_vote)
        existing_vote.structure_explanation = str(flower_vote.structure_explanation)
        existing_vote.nose_vote = float(flower_vote.nose_vote)
        existing_vote.nose_explanation = str(flower_vote.nose_explanation)
        existing_vote.flavor_vote = float(flower_vote.flavor_vote)
        existing_vote.flavor_explanation = str(flower_vote.flavor_explanation)
        existing_vote.effects_vote = float(flower_vote.effects_vote)
        existing_vote.effects_explanation = str(flower_vote.effects_explanation)
        existing_vote.created_at = date_handler(datetime.datetime.now())
        try:
            db.commit()
            db.refresh(existing_vote)
            return existing_vote
        except:
            db.rollback()
            raise
    else:
        # Add new vote
        return add_new_flower_vote(flower_vote, db)
