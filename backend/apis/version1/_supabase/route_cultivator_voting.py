#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jun  2 11:29:26 2024

@author: dale
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from db.session import get_db
from db.repository.unique_cultivators import (
    create_cultivator_for_voting,
    get_all_cultivator_votes,
    create_cultivator_vote,
    delete_cultivator_vote_for_user,
    decode_base64_email,
    get_all_unique_cultivators
)
from schemas.unique_cultivators import (
    UniqueCultivatorCreate,
    UniqueCultivatorResponse,
    CultivatorVoteCreate,
    CultivatorVoteResponse,
    ListCultivatorVotingResponse,
    UniqueCultivatorOptionsResponse,
)

router = APIRouter()


@router.post("/add_new", response_model=UniqueCultivatorResponse)
async def create_cultivator(
    cultivator: UniqueCultivatorCreate, db: Session = Depends(get_db)
):
    return create_cultivator_for_voting(db, cultivator)


@router.get("/get_votes", response_model=ListCultivatorVotingResponse)
async def list_votes(db: Session = Depends(get_db)):
    return get_all_cultivator_votes(db)


@router.post("/add_vote", response_model=CultivatorVoteResponse)
async def vote_for_cultivator(vote: CultivatorVoteCreate, db: Session = Depends(get_db)):
    return create_cultivator_vote(db, vote)


@router.delete(
    "/{encoded_email}/{cultivator_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_vote_for_cultivator(
    encoded_email: str, cultivator_id: int, db: Session = Depends(get_db)
):
    decoded_email = decode_base64_email(encoded_email)
    delete_cultivator_vote_for_user(db, decoded_email, cultivator_id)
    return True


@router.get("/cultivators", response_model=UniqueCultivatorOptionsResponse)
async def list_unique_cultivators(db: Session = Depends(get_db)):
    cultivators = get_all_unique_cultivators(db)
    return UniqueCultivatorOptionsResponse(cultivators=cultivators)
