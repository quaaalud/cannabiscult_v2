#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 13 19:39:28 2023

@author: dale
"""

from pydantic import BaseModel, EmailStr, Field

class CreateMysteryFlowerReview(BaseModel):
    cultivator: str = Field(
        ..., 
        description="Name of the cultivator", 
        max_length=255
    )
    strain: str = Field(
        ..., description="Strain of the flower", max_length=255
    )
    voter_email: EmailStr = Field(
        ..., description="Email of the voter"
    )
    method_of_consumption: str = Field(
        None, description="Method of consumption", max_length=255
    )
    mystery_sight_vote: str = Field(
        None, description="Vote for sight"
    )
    mystery_sight_explanation: str = Field(
        None, description="Explanation for sight vote", max_length=255
    )
    mystery_structure_vote: str = Field(
        None, description="Vote for structure"
    )
    mystery_structure_explanation: str = Field(
        None, description="Explanation for structure vote", max_length=255
    )
    mystery_smell_vote: str = Field(
        None, description="Vote for smell"
    )
    mystery_smell_explanation: str = Field(
        None, description="Explanation for smell vote", max_length=255
    )
    mystery_freshness_vote: str = Field(
        None, description="Vote for freshness"
    )
    mystery_freshness_explanation: str = Field(
        None, description="Explanation for freshness vote", max_length=255
    )
    mystery_flavor_vote: str = Field(
        None, description="Vote for flavor"
    )
    mystery_flavor_explanation: str = Field(
        None, description="Explanation for flavor vote", max_length=255
    )
    mystery_effects_vote: str = Field(
        None, description="Vote for effects")
    mystery_effects_explanation: str = Field(
        None, description="Explanation for effects vote", max_length=255
    )
    mystery_smoothness_vote: str = Field(
        None, description="Vote for smoothness"
    )
    mystery_smoothness_explanation: str = Field(
        None, description="Explanation for smoothness vote", max_length=255
    )
