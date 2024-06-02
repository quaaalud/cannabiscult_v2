#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jun  2 10:53:34 2024

@author: dale
"""

from typing import List, Optional, Union
from pydantic import BaseModel, Field, EmailStr


class UniqueCultivatorCreate(BaseModel):
    cultivator: str = Field(
        ...,
        description="Cultivator's name for submission in tournament participation.",
        max_length=100,
    )

    class Config:
        from_attributes = True


class UniqueCultivatorResponse(BaseModel):
    id: int = Field(..., description="Cultivator ID value")
    cultivator: str = Field(
        ...,
        description="Cultivator's name for submission in tournament participation.",
        max_length=100,
    )

    class Config:
        from_attributes = True


class CultivatorVoteCreate(BaseModel):
    cultivator_id: int = Field(..., description="Cultivator ID value")
    email: Union[EmailStr, str] = Field(..., description="The current voter's email address")

    class Config:
        from_attributes = True


class CultivatorVoteResponse(BaseModel):
    cultivator: str = Field(
        ...,
        description="Cultivator's name for submission in tournament participation.",
        max_length=100,
    )
    email: str = Field(..., description="The current voter's email address")

    class Config:
        from_attributes = True


class UniqueCultivatorInfo(BaseModel):
    id: int = Field(..., description="Cultivator ID value")
    cultivator: str = Field(..., description="Cultivator's name")
    voting: Optional[List[dict]] = Field(..., description="List of related votes")

    class Config:
        from_attributes = True


class CultivatorVotingResponse(BaseModel):
    id: int = Field(..., description="Vote ID")
    cultivator_id: int = Field(..., description="Cultivator ID value")
    email: str = Field(..., description="Voter's email")
    cultivator_name: str = Field(..., description="Cultivator's name")

    class Config:
        from_attributes = True


class ListCultivatorVotingResponse(BaseModel):
    cultivator_votes: List[CultivatorVotingResponse]


class UniqueCultivatorOption(BaseModel):
    id: int = Field(..., description="Cultivator ID value")
    cultivator: str = Field(..., description="Cultivator's name")

    class Config:
        from_attributes = True


class UniqueCultivatorOptionsResponse(BaseModel):
    cultivators: List[UniqueCultivatorOption]
