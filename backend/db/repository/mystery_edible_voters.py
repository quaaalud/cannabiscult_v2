#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 30 21:05:19 2023

@author: dale
"""

from sqlalchemy.orm import Session
from schemas.mystery_edible_voters import MysteryEdibleVoterCreate
from db.models.mystery_edible_voters import MysteryEdibleVoter
import datetime


def date_handler(obj):
    if isinstance(obj, datetime.date):
        return obj.isoformat()
    else:
        raise TypeError("Type %s not serializable" % type(obj))
        
        
def create_mystery_edible_voter(
        voter: MysteryEdibleVoterCreate,
        db:Session):
    voter = MysteryEdibleVoter(
        email = str(voter.email).lower(),
        name = str(voter.name),
        zip_code = str(voter.zip_code),
        phone = str(voter.phone),
        agree_tos=True,
        date_posted=date_handler(datetime.datetime.now())
    )
    try:
        db.add(voter)
    except:
        db.rollback()
    else:
        db.commit()
        db.refresh(voter)
    finally:
        return voter