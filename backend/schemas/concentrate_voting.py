#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep  4 17:20:10 2023

@author: dale
"""

from pydantic import BaseModel


class ConcentrateVoteCreate(BaseModel):
    cultivator_selected: str
    strain_selected: str
    structure_vote: str
    structure_explanation: str
    nose_vote: float
    nose_explanation: str
    flavor_vote: float
    flavor_explanation: str
    effects_vote: float
    effects_explanation: str
    user_email: str