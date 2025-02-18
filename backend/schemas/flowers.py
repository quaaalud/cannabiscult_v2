#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov  5 16:47:38 2023

@author: dale
"""

from pydantic import BaseModel, EmailStr, Field, StringConstraints
from typing import List, Optional, Annotated
from schemas.product_types import StrainCategoryEnum, StrainType


RatingType = Annotated[float, Field(gt=0, lt=10.1)]
OptionalStr = Annotated[Optional[str], Field(None, max_length=1500)]


class FlowersBase(BaseModel):
    flower_id: int = Field(..., description="Unique identifier for the flower")
    cultivator: str = Field(..., description="Name of the cultivator")
    strain: str = Field(..., description="Name of the strain")
    is_mystery: bool = Field(..., description="Indicates if the flower is a mystery")
    card_path: str = Field(..., description="Path to the flower's image card")
    voting_open: bool = Field(True, description="Indicates if voting is open for this flower")
    product_type: str = Field("flower", description="Type of the product, default is 'flower'")

    class Config:
        populate_by_name = True
        from_attributes = True
        strip_whitespace = True
        exclude_unset = True


class FlowerDescriptionBase(BaseModel):
    flower_id: int = Field(None, description="Unique identifier for the flower")
    description: Annotated[str, StringConstraints(max_length=1500)] = Field(
        "Coming Soon", description="Description of the flower, max 1500 characters"
    )
    effects: Annotated[str, StringConstraints(max_length=1500)] = Field(
        "Coming Soon", description="Effects of the flower, max 1500 characters"
    )
    lineage: Annotated[str, StringConstraints(max_length=1500)] = Field(
        "Coming Soon", description="Lineage of the flower, max 1500 characters"
    )
    terpenes_list: Optional[List[str]] = Field(None, description="List of terpenes in the flower")
    cultivar_email: EmailStr = Field(..., description="Email of the cultivar")
    strain_category: StrainCategoryEnum = Field(
        StrainCategoryEnum.cult_pack, description="The category for the flower strain. ex: indica, hybrid, etc."
    )

    class Config:
        from_attributes = True
        use_enum_values = True
        strip_whitespace = True
        exclude_unset = True


class AddFlowerDescription(FlowerDescriptionBase):
    pass


class GetFlowerWithDescription(BaseModel):
    flower_id: int = Field(..., description="Unique identifier for the flower")
    cultivator: str = Field(..., description="Name of the cultivator")
    strain: str = Field(..., description="Name of the strain")
    is_mystery: bool = Field(..., description="Indicates if the flower is a mystery")
    url_path: str = Field(..., description="Path to the flower's image card")
    voting_open: bool = Field(True, description="Indicates if voting is open for this flower")
    product_type: str = Field("flower", description="Type of the product, default is 'flower'")

    description_id: int = Field(..., description="Unique identifier for the flower description")
    description_text: Annotated[str, StringConstraints(max_length=1500)] = Field(
        "Coming Soon", description="Description of the flower, max 1500 characters"
    )
    effects: Annotated[str, StringConstraints(max_length=1500)] = Field(
        "Coming Soon", description="Effects of the flower, max 1500 characters"
    )
    lineage: Annotated[str, StringConstraints(max_length=1500)] = Field(
        "Coming Soon", description="Lineage of the flower, max 1500 characters"
    )
    terpenes_list: Optional[List[str]] = Field(None, description="List of terpenes in the flower")
    cultivar: Optional[EmailStr] = Field(None, description="Email of the cultivar")
    username: Optional[str] = Field("", description="Username of the cultivar")
    strain_category: StrainCategoryEnum = Field(
        StrainCategoryEnum.cult_pack, description="The category for the flower strain. ex: indica, hybrid, etc."
    )

    class Config:
        from_attributes = True
        use_enum_values = True
        strip_whitespace = True
        exclude_unset = True


class FlowerRankingBase(BaseModel):
    strain: str
    appearance_rating: float = Field(..., gt=0, lt=10.1)
    freshness_rating: float = Field(..., gt=0, lt=10.1)
    smell_rating: float = Field(..., gt=0, lt=10.1)
    flavor_rating: float = Field(..., gt=0, lt=10.1)
    harshness_rating: float = Field(..., gt=0, lt=10.1)
    effects_rating: float = Field(..., gt=0, lt=10.1)
    appearance_explanation: Optional[str] = Field(None, max_length=1500)
    freshness_explanation: Optional[str] = Field(None, max_length=1500)
    flavor_explanation: Optional[str] = Field(None, max_length=1500)
    smell_explanation: Optional[str] = Field(None, max_length=1500)
    harshness_explanation: Optional[str] = Field(None, max_length=1500)
    effects_explanation: Optional[str] = Field(None, max_length=1500)

    pack_code: Optional[str] = Field(None, max_length=99)
    flower_id: int = Field(...)

    class Config:
        from_attributes = True
        strip_whitespace = True
        populate_by_name = True
        exclude_unset = True


class CreateFlowerRanking(FlowerRankingBase):
    cultivator: str
    method_of_consumption: str = Field(..., description="Method of Connsumption for the reviewed strain.")
    connoisseur: EmailStr = Field(..., description="Email address of the connoisseur")


class GetFlowerRanking(CreateFlowerRanking):
    strain: str
    cultivator: str
    method_of_consumption: str = Field(..., description="Method of Connsumption for the reviewed strain.")
    connoisseur: Optional[EmailStr] = Field(
        "cultmember@cannabiscult.co", description="Email address of the connoisseur"
    )
    username: Optional[str] = Field("Cult Member", description="User name for the connoisseur")
    appearance_rating: float = Field(..., gt=0, lt=10.1)
    freshness_rating: float = Field(..., gt=0, lt=10.1)
    smell_rating: float = Field(..., gt=0, lt=10.1)
    flavor_rating: float = Field(..., gt=0, lt=10.1)
    harshness_rating: float = Field(..., gt=0, lt=10.1)
    effects_rating: float = Field(..., gt=0, lt=10.1)
    appearance_explanation: Optional[str] = Field(None, max_length=1500)
    freshness_explanation: Optional[str] = Field(None, max_length=1500)
    flavor_explanation: Optional[str] = Field(None, max_length=1500)
    smell_explanation: Optional[str] = Field(None, max_length=1500)
    harshness_explanation: Optional[str] = Field(None, max_length=1500)
    effects_explanation: Optional[str] = Field(None, max_length=1500)

    pack_code: Optional[str] = Field(None, max_length=99)
    flower_id: int = Field(...)

    class Config:
        from_attributes = True
        strip_whitespace = True
        populate_by_name = True
        exclude_unset = True


class FlowerRankingValuesSchema(BaseModel):
    flower_ranking_id: int
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
