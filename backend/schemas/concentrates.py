#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov  5 16:47:38 2023

@author: dale
"""

from pydantic import BaseModel, Field, StringConstraints, validator, root_validator, EmailStr, confloat
from typing import Optional, Union, Annotated, List
from schemas.product_types import StrainCategoryEnum, StrainType


OptionalStr = Annotated[Optional[str], Field(None, max_length=500)]


class ConcentratesBase(BaseModel):
    concentrate_id: int = Field(..., description="Unique identifier for the concentrate")
    cultivator: Annotated[str, StringConstraints(max_length=500)] = Field(..., description="Name of the cultivator")
    strain: Annotated[str, StringConstraints(max_length=500)] = Field(..., description="Name of the strain")
    is_mystery: bool = Field(..., description="Indicates if the concentrate is a mystery product")
    card_path: Annotated[str, StringConstraints(max_length=500)] = Field(
        ..., description="Path to the concentrate's image card"
    )
    voting_open: bool = Field(True, description="Indicates if voting is open for this concentrate")

    @validator("cultivator", "strain", pre=True, always=True)
    def verify_string_and_capitalize_cultivator(cls, v):
        return v.title() if isinstance(v, str) else "Cultivar"

    @validator("strain", pre=True, always=True)
    def verify_string_and_capitalize_strain(cls, v):
        return v.title() if isinstance(v, str) else "CC #"

    class Config:
        from_attributes = True
        strip_whitespace = True
        populate_by_name = True


class HiddenConcentrate(ConcentratesBase):
    pass

    @root_validator(pre=True)
    def mask_cultivator(cls, values):
        if values.get("is_mystery", False):
            values["cultivator"] = "Cultivar"
        return values


class ConcentrateRankingBase(BaseModel):
    cultivator: str = Field(..., description="Name of the cultivator")
    strain: str = Field(..., description="Name of the strain")
    color_rating: confloat(gt=0, lt=10.1) = Field(..., description="Color rating, range 0-10")
    consistency_rating: confloat(gt=0, lt=10.1) = Field(..., description="Consistency rating, range 0-10")
    smell_rating: confloat(gt=0, lt=10.1) = Field(..., description="Smell rating, range 0-10")
    flavor_rating: confloat(gt=0, lt=10.1) = Field(..., description="Flavor rating, range 0-10")
    harshness_rating: confloat(gt=0, lt=10.1) = Field(..., description="Harshness rating, range 0-10")
    residuals_rating: confloat(gt=0, lt=10.1) = Field(..., description="Residuals rating, range 0-10")
    effects_rating: confloat(gt=0, lt=10.1) = Field(..., description="Effects rating, range 0-10")
    color_explanation: Optional[str] = Field(None, max_length=500, description="Explanation for the color rating")
    consistency_explanation: OptionalStr = Field(
        None, max_length=500, description="Explanation for the consistency rating"
    )
    flavor_explanation: OptionalStr = Field(None, max_length=500, description="Explanation for the flavor rating")
    smell_explanation: OptionalStr = Field(None, max_length=500, description="Explanation for the smell rating")
    harshness_explanation: OptionalStr = Field(
        None, max_length=500, description="Explanation for the harshness rating"
    )
    residuals_explanation: OptionalStr = Field(
        None, max_length=500, description="Explanation for the residuals rating"
    )
    effects_explanation: OptionalStr = Field(None, max_length=500, description="Explanation for the effects rating")
    pack_code: OptionalStr = Field(None, max_length=99, description="Pack code of the concentrate, if provided")

    @validator("pack_code", pre=True, always=True)
    def strip_whitespace(cls, v):
        return v.strip() if isinstance(v, str) else v

    class Config:
        from_attributes = True
        populate_by_name = True
        strip_whitespace = True
        exclude_unset = True


class CreateConcentrateRanking(ConcentrateRankingBase):
    connoisseur: EmailStr = Field(..., description="Email of the connoisseur")
    concentrate_id: Union[int, str] = Field(..., description="Unique identifier for the concentrate")


class GetConcentrateRanking(CreateConcentrateRanking):
    class Config:
        from_attributes = True
        populate_by_name = True


class CreateHiddenConcentrateRanking(CreateConcentrateRanking):
    pass


class HiddenConcentrateRanking(CreateHiddenConcentrateRanking):
    pass


class GetConcentrateWithDescription(BaseModel):
    concentrate_id: int = Field(..., description="Unique identifier for the concentrate")
    cultivator: StrainType = Field(..., description="Name of the cultivator")
    strain: StrainType = Field(..., description="Name of the strain")
    is_mystery: bool = Field(..., description="Indicates if the concentrate is a mystery")
    url_path: str = Field(..., description="Path to the concentrate's image card")
    voting_open: bool = Field(True, description="Indicates if voting is open for this concentrate")
    product_type: str = Field("concentrate", description="Type of the product, default is 'concentrate'")

    description_id: int = Field(..., description="Unique identifier for the concentrate description")
    description_text: Annotated[str, StringConstraints(max_length=500)] = Field(
        "Coming Soon", description="Description of the concentrate, max 1500 characters"
    )
    effects: Annotated[str, StringConstraints(max_length=500)] = Field(
        "Coming Soon", description="Effects of the concentrate, max 1500 characters"
    )
    lineage: Annotated[str, StringConstraints(max_length=500)] = Field(
        "Coming Soon", description="Lineage of the concentrate, max 1500 characters"
    )
    terpenes_list: Optional[List[str]] = Field(None, description="List of terpenes in the concentrate")
    cultivar: EmailStr = Field(..., description="Email of the cultivar")
    username: Optional[str] = Field("", description="Username of the cultivar")
    strain_category: StrainCategoryEnum = Field(
        StrainCategoryEnum.cult_pack, description="The category for the concentrate strain. ex: indica, hybrid, etc."
    )

    class Config:
        from_attributes = True
        use_enum_values = True
        strip_whitespace = True
        exclude_unset = True


class ConcentrateRankingValuesSchema(BaseModel):
    concentrate_ranking_id: int
    overall_score: float = Field(..., gt=0, lt=10.1)
    appearance_rating: float = Field(..., gt=0, lt=10.1)
    freshness_rating: float = Field(..., gt=0, lt=10.1)
    smell_rating: float = Field(..., gt=0, lt=10.1)
    flavor_rating: float = Field(..., gt=0, lt=10.1)
    harshness_rating: float = Field(..., gt=0, lt=10.1)
    effects_rating: float = Field(..., gt=0, lt=10.1)

    class Config:
        from_attributes = True
        populate_by_name = True
        exclude_unset = True
