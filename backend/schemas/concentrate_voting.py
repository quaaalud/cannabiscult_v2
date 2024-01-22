#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep  4 17:20:10 2023

@author: dale
"""

from pydantic import BaseModel, Field, EmailStr, constr, confloat


class ConcentrateVoteCreate(BaseModel):
    cultivator_selected: str = Field(..., description="Selected cultivator's name")
    strain_selected: str = Field(..., description="Selected strain's name")
    structure_vote: confloat(ge=0, le=10) = Field(
        ..., description="Vote for the concentrate structure, from 0 to 10"
    )
    structure_explanation: constr(max_length=500) = Field(
        ..., description="Explanation for the structure vote"
    )
    nose_vote: confloat(ge=0, le=10) = Field(
        ..., description="Vote for the concentrate nose/fragrance, from 0 to 10"
    )
    nose_explanation: constr(max_length=500) = Field(
        ..., description="Explanation for the nose vote"
    )
    flavor_vote: confloat(ge=0, le=10) = Field(
        ..., description="Vote for the concentrate flavor, from 0 to 10"
    )
    flavor_explanation: constr(max_length=500) = Field(
        ..., description="Explanation for the flavor vote"
    )
    effects_vote: confloat(ge=0, le=10) = Field(
        ..., description="Vote for the concentrate effects, from 0 to 10"
    )
    effects_explanation: constr(max_length=500) = Field(
        ..., description="Explanation for the effects vote"
    )
    user_email: EmailStr = Field(..., description="Email address of the user")

