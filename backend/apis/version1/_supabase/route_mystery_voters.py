#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 11 22:10:32 2023

@author: dale
"""


from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.session import get_db
from schemas.mystery_voters import MysteryVoterCreate, StrainGuessInput
from db.repository.mystery_voters import create_new_voter, add_strain_guess
from db.models.mystery_voters import MysteryVoter


router = APIRouter()


@router.post("/", response_model=None)
def create_mystery_voter(voter: MysteryVoterCreate, db: Session = Depends(get_db)) -> MysteryVoter:
    voter = create_new_voter(voter=voter, db=db)
    return voter


@router.post("/", response_model=None)
def get_voter_info_by_email(voter_email: str, db: Session = Depends(get_db)):

    voter = db.query(MysteryVoter).filter(MysteryVoter.email == voter_email).first()

    if not voter:
        return None

    return voter


@router.post("/submit_strain_guesses/")
async def submit_strain_guess(guess_input: StrainGuessInput, db: Session = Depends(get_db)):
    try:
        new_guess = add_strain_guess(db, guess_input.strain_guesses, guess_input.email)
        return new_guess
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
