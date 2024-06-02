#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jun  2 10:26:09 2024

@author: dale
"""

import base64
from typing import List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from db.models.unique_cultivators import UniqueCultivators, CultivatorVoting
from schemas.unique_cultivators import (
    UniqueCultivatorCreate,
    UniqueCultivatorResponse,
    CultivatorVoteCreate,
    CultivatorVoteResponse,
    CultivatorVotingResponse,
    UniqueCultivatorInfo,
    UniqueCultivatorOption,
    ListCultivatorVotingResponse,
)
from schemas.users import UserEmailSchema


def decode_base64_email(encoded_email: str) -> str:
    try:
        # Decode the base64 encoded string
        decoded_bytes = base64.urlsafe_b64decode(encoded_email)
        decoded_email = decoded_bytes.decode("utf-8")
        return decoded_email
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid base64 encoded email: {e}",
        )


def encode_base64_email(user_email: str) -> str:
    encoded_bytes = base64.urlsafe_b64encode(user_email.encode("utf-8"))
    encoded_email = encoded_bytes.decode("utf-8")
    return encoded_email


# Create a new cultivator, ensuring no duplicates
def create_cultivator_for_voting(
    db: Session, cultivator: UniqueCultivatorCreate
) -> UniqueCultivatorResponse:
    existing_cultivator = (
        db.query(UniqueCultivators)
        .filter(UniqueCultivators.cultivator == cultivator.cultivator)
        .first()
    )
    if existing_cultivator:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Cultivator already exists."
        )

    new_cultivator = UniqueCultivators(cultivator=cultivator.cultivator)
    db.add(new_cultivator)
    try:
        db.commit()
        db.refresh(new_cultivator)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create new cultivator.",
        )

    return UniqueCultivatorResponse(
        id=new_cultivator.id, cultivator=new_cultivator.cultivator
    )


# Read all cultivator votes
def get_all_cultivator_votes(db: Session) -> ListCultivatorVotingResponse:
    votes = db.query(CultivatorVoting).options(
        joinedload(CultivatorVoting.cultivator_info),
        joinedload(CultivatorVoting.voter_info)
    ).all()

    if not votes:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No votes found."
        )

    cultivator_votes = [
        CultivatorVotingResponse(
            id=vote.id,
            cultivator_id=vote.cultivator_info.id,
            email=encode_base64_email(vote.email),
            cultivator_name=vote.cultivator_info.cultivator
        ) for vote in votes
    ]
    return ListCultivatorVotingResponse(cultivator_votes=cultivator_votes)


# Create a new vote
def create_cultivator_vote(
    db: Session, vote: CultivatorVoteCreate
) -> CultivatorVoteResponse:
    try:
        decoded_email = decode_base64_email(vote.email)
    except Exception:
        validated_email = UserEmailSchema(email=vote.email)
        decoded_email = validated_email.email
    existing_vote = db.query(CultivatorVoting).filter(
        CultivatorVoting.email == decoded_email,
        CultivatorVoting.cultivator_id == vote.cultivator_id
    ).first()

    if existing_vote:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already voted for this cultivator."
        )
    new_vote = CultivatorVoting(cultivator_id=vote.cultivator_id, email=decoded_email)
    db.add(new_vote)
    try:
        db.commit()
        db.refresh(new_vote)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cast vote.",
        )

    return CultivatorVoteResponse(
        cultivator=new_vote.cultivator_info.cultivator,
        email=encode_base64_email(new_vote.email),
    )


# Delete a cultivator by ID
def delete_cultivator_vote_for_user(db: Session, user_email: str, cultivator_id) -> None:
    cultivator_vote = (
        db.query(CultivatorVoting)
        .filter(
            CultivatorVoting.email == user_email
            and CultivatorVoting.cultivator_id == cultivator_id
        )
        .first()
    )
    if not cultivator_vote:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Cultivator vote not found."
        )

    db.delete(cultivator_vote)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete cultivator vote.",
        )


def get_all_unique_cultivators(db: Session) -> List[UniqueCultivatorOption]:
    cultivators = db.query(UniqueCultivators).order_by(UniqueCultivators.cultivator).all()
    if not cultivators:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No cultivators found."
        )

    return [
        UniqueCultivatorOption(id=cultivator.id, cultivator=cultivator.cultivator)
        for cultivator in cultivators
    ]
