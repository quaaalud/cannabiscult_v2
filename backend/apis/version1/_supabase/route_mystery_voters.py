#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 11 22:10:32 2023

@author: dale
"""

from typing import Optional, Dict
from fastapi import APIRouter, Form, Depends
from sqlalchemy.orm import Session
from db.session import get_db
from schemas.mystery_voters import MysteryVoterCreate
from db.repository.mystery_voters import create_new_voter
from db.models.myster_voters import MysteryVoter


router = APIRouter()


@router.post("/")
def create_mystery_voter(
    voter: MysteryVoterCreate,
    db: Session = Depends(get_db)
):
    voter = create_new_voter(
        voter=voter,
        db=db
    )
    return voter
  
@router.post("/submit-new-voter")
def submit_mystery_voter_create(
      voter_name: str = Form('None'),
      voter_email: str = Form(...),
      voter_phone: str = Form('None'),
      voter_zip_code: str = Form('None'),
      db: Session = Depends(get_db),
) -> Optional[bool]:
    voter = MysteryVoterCreate(
        name=voter_name,
        email=voter_email,
        phone=voter_phone,
        voter=voter_zip_code,
    )
    if not voter:
        return None
      
    create_mystery_voter(voter=voter, db=db)
    return True


@router.get("/check-myster-voter", response_model=Optional[Dict[str, str]])  
def get_voter_info_email_by_math(
      voter_email: str,
      db: Session = Depends(get_db)
) -> Optional[Dict[str, str]]:
    voter = db.query(
        MysteryVoter
    ).filter(MysteryVoter.email == voter_email).first()
    
    if not voter:
        return None
    
    return {'voter_email': voter.email}
    
