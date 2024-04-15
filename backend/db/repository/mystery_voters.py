#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 11 21:51:54 2023

@author: dale
"""

from sqlalchemy.orm import Session
from typing import Union
from core.config import settings
from schemas.mystery_voters import MysteryVoterCreate
from db.models.mystery_voters import MysteryVoter, StrainGuess
import datetime
import json


def date_handler(obj):
    if isinstance(obj, datetime.date):
        return obj.isoformat()
    else:
        raise TypeError("Type %s not serializable" % type(obj))


@settings.retry_db
def create_new_voter(voter: MysteryVoterCreate, db: Session) -> Union[MysteryVoter, None]:
    new_voter_data = {
        "email": str(voter.email),
        "name": str(voter.name),
        "zip_code": str(voter.zip_code),
        "phone": str(voter.phone),
        "agree_tos": True,
        "date_posted": date_handler(datetime.datetime.now()),
    }

    # Handle optional fields
    if voter.industry_employer is not None:
        new_voter_data["industry_employer"] = str(voter.industry_employer)
    if voter.industry_job_title is not None:
        new_voter_data["industry_job_title"] = str(voter.industry_job_title)

    new_voter = MysteryVoter(**new_voter_data)
    try:
        db.add(new_voter)
        db.commit()
        db.refresh(new_voter)
        return new_voter
    except Exception as e:
        print(e)
        db.rollback()
        return None


@settings.retry_db
def add_strain_guess(db: Session, guess_data: dict, user_email: str):
    """
    Adds a new strain guess to the database.

    :param db: SQLAlchemy Session object
    :param guess_data: Dictionary containing strain guesses
    :param user_email: Email of the user making the guess
    """
    try:
        # Convert guess data to JSON format
        strain_guesses_json = json.dumps(guess_data)

        # Create a new StrainGuess object
        new_guess = StrainGuess(strain_guesses=strain_guesses_json, email=user_email)

        # Add the new object to the session and commit
        db.add(new_guess)
        db.commit()
        db.refresh(new_guess)

        return new_guess

    except Exception as e:
        db.rollback()
        raise e
