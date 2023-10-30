#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 30 19:40:53 2023

@author: dale
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class EdibleVoteBase(BaseModel):
    cultivator: str 
    strain: str
    voter_email: EmailStr = Field(..., max_length=500)
    appearance_vote: float = Field(..., gt=0, lt=10)
    smell_vote: float = Field(..., gt=0, lt=10)
    flavor_vote: float = Field(..., gt=0, lt=10)
    aftertaste_vote: float = Field(..., gt=0, lt=10)
    effects_vote: float = Field(..., gt=0, lt=10)
    appearance_explanation: Optional[str] = Field(None, max_length=500)
    flavor_explanation: Optional[str] = Field(None, max_length=500)
    aftertaste_explanation: Optional[str] = Field(None, max_length=500)
    effects_explanation: Optional[str] = Field(None, max_length=500)

class EdibleVoteCreate(EdibleVoteBase):
    pass

class EdibleVote(EdibleVoteBase):
    edible_vote_id: int
    review_id: int
    created_at: str
    class Config:
        from_attributes = True