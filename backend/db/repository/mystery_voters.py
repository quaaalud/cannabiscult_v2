#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 11 21:51:54 2023

@author: dale
"""

from sqlalchemy.orm import Session
from schemas.mystery_voters import MysteryVoterCreate
from db.models.mystery_voters import MysteryVoter
import datetime


def date_handler(obj):
    if isinstance(obj, datetime.date):
        return obj.isoformat()
    else:
        raise TypeError("Type %s not serializable" % type(obj))
        
        
def create_new_voter(
        voter: MysteryVoterCreate,
        db:Session):
    voter = MysteryVoter(
        email = str(voter.email),
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