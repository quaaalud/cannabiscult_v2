#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 30 21:15:57 2023

@author: dale
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.session import get_db
from schemas.mystery_edible_voters import MysteryEdibleVoterCreate
from db.repository.mystery_edible_voters import create_mystery_edible_voter
from db.models.mystery_edible_voters import MysteryEdibleVoter


router = APIRouter()


@router.post("/submit-mystery-edible-voter", response_model=None)
def submit_new_mystery_edible_voter(
    voter: MysteryEdibleVoterCreate,
    db: Session = Depends(get_db)
) -> MysteryEdibleVoter:
    voter = create_mystery_edible_voter(
        voter=voter,
        db=db
    )
    return voter


@router.post("/get-edible-voter-by-email", response_model=None)  
def get_mystery_edible_voter_by_email(
      voter_email: str,
      db: Session = Depends(get_db)
):  
    voter = db.query(
        MysteryEdibleVoter
    ).filter(
        MysteryEdibleVoter.email == voter_email
    ).first()
    
    if not voter:
        return None
    
    return voter
