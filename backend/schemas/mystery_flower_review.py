#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 13 19:39:28 2023

@author: dale
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class CreateMysteryFlowerReview(BaseModel):
    cultivator: str = Field(..., description="Name of the cultivator")
    strain: str = Field(..., description="Name of the strain")
    voter_email: EmailStr = Field(..., description="Email address of the voter")
    method_of_consumption: str = Field(..., description="Method used to consume the flower")
    mystery_size_vote: int = Field(..., description="Vote for the mystery size")
    mystery_size_explanation: Optional[str] = Field(
        None, description="Explanation for the mystery size vote"
    )
    mystery_structure_vote: int = Field(..., description="Vote for the mystery structure")
    mystery_structure_explanation: Optional[str] = Field(
        None, description="Explanation for the mystery structure vote"
    )
    mystery_smell_vote: int = Field(..., description="Vote for the mystery smell")
    mystery_smell_explanation: Optional[str] = Field(
        None, description="Explanation for the mystery smell vote"
    )
    mystery_freshness_vote: int = Field(..., description="Vote for the mystery freshness")
    mystery_freshness_explanation: Optional[str] = Field(
        None, description="Explanation for the mystery freshness vote"
    )
    mystery_flavor_vote: int = Field(..., description="Vote for the mystery flavor")
    mystery_flavor_explanation: Optional[str] = Field(
        None, description="Explanation for the mystery flavor vote"
    )
    mystery_effects_vote: int = Field(..., description="Vote for the mystery effects")
    mystery_effects_explanation: Optional[str] = Field(
        None, description="Explanation for the mystery effects vote"
    )
    mystery_smoothness_vote: int = Field(..., description="Vote for the mystery smoothness")
    mystery_smoothness_explanation: Optional[str] = Field(
        None, description="Explanation for the mystery smoothness vote"
    )
