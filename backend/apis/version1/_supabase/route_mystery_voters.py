#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 11 22:10:32 2023

@author: dale
"""

from typing import Optional
from fastapi import APIRouter, Form, Depends
from sqlalchemy.orm import Session
from db.session import get_db
from schemas.mystery_voters import MysteryVoterCreate
from db.repository.mystery_voters import create_new_voter
from db.models.mystery_voters import MysteryVoter


router = APIRouter()


@router.post("/", response_model=None)
def create_mystery_voter(
    voter: MysteryVoterCreate,
    db: Session = Depends(get_db)
) -> MysteryVoter:
    voter = create_new_voter(
        voter=voter,
        db=db
    )
    return voter


@router.post("/", response_model=None)  
def get_voter_info_by_email(
      voter_email: str,
      db: Session = Depends(get_db)
):
    
    voter = db.query(
        MysteryVoter
    ).filter(
        MysteryVoter.email == voter_email
    ).first()
    
    if not voter:
        return None
    
    return voter
