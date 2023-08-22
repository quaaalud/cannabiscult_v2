#!/usr/bin/env python3

from pydantic import BaseModel


class FlowerVoteCreate(BaseModel):
    cultivator_selected: str
    strain_selected: str
    structure_explanation: str
    nose_vote: float
    nose_explanation: str
    flavor_vote: float
    flavor_explanation: str
    effects_vote: float
    effects_explanation: str
    user_email: str

