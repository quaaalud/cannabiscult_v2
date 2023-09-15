#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 13 19:39:28 2023

@author: dale
"""

from pydantic import BaseModel, EmailStr


class CreateMysteryFlowerReview(BaseModel):
    cultivator: str 
    strain: str
    voter_email: EmailStr
    method_of_consumption: str
    mystery_sight_vote: int
    mystery_sight_explanation: str
    mystery_structure_vote: int
    mystery_structure_explanation: str
    mystery_smell_vote: int
    mystery_smell_explanation: str
    mystery_freshness_vote: int
    mystery_freshness_explanation: str
    mystery_flavor_vote: int
    mystery_flavor_explanation: str
    mystery_effects_vote: int
    mystery_effects_explanation: str
    mystery_smoothness_vote: int
    mystery_smoothness_explanation: str
