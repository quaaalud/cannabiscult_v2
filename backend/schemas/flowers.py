#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov  5 16:47:38 2023

@author: dale
"""

from pydantic import BaseModel, confloat, EmailStr, root_validator, Field, validator, StringConstraints
from typing import List, Optional, Annotated
import enum


StrainType = Annotated[str, Annotated[str, StringConstraints(min_length=1, max_length=500)]]
RatingType = Annotated[float, Field(gt=0, lt=10.1)]
OptionalStr = Annotated[Optional[str], Field(None, max_length=500)]


class StrainCategoryEnum(str, enum.Enum):
    INDICA = "indica"
    INDICA_HYBRID = "indica_dominant_hybrid"
    HYBRID = "hybrid"
    SATICA_HYBRID = "sativa_dominant_hybrid"
    SATIVA = "sativa"


class FlowersBase(BaseModel):
    flower_id: int = Field(..., description="Unique identifier for the flower")
    cultivator: str = Field(..., description="Name of the cultivator")
    strain: str = Field(..., description="Name of the strain")
    is_mystery: bool = Field(..., description="Indicates if the flower is a mystery")
    card_path: str = Field(..., description="Path to the flower's image card")
    voting_open: bool = Field(True, description="Indicates if voting is open for this flower")
    product_type: str = Field("flower", description="Type of the product, default is 'flower'")

    @validator("cultivator", "strain", pre=True, always=True)
    def verify_string_and_capitalize_name(cls, v):
        return v.capitalize() if isinstance(v, str) else None

    class Config:
        populate_by_name = True
        from_attributes = True
        strip_whitespace = True
        exclude_unset = True


class HiddenFlower(FlowersBase):
    @root_validator(pre=True)
    def mask_cultivator(cls, values):
        if values.get("is_mystery", False):
            values["cultivator"] = "Hidden"
        return values


class FlowerDescriptionBase(BaseModel):
    flower_id: int = Field(None, description="Unique identifier for the flower")
    description: Annotated[str, StringConstraints(max_length=500)] = Field(
        "Coming Soon", description="Description of the flower, max 1500 characters"
    )
    effects: Annotated[str, StringConstraints(max_length=500)] = Field(
        "Coming Soon", description="Effects of the flower, max 1500 characters"
    )
    lineage: Annotated[str, StringConstraints(max_length=500)] = Field(
        "Coming Soon", description="Lineage of the flower, max 1500 characters"
    )
    terpenes_list: Optional[List[str]] = Field(None, description="List of terpenes in the flower")
    cultivar_email: EmailStr = Field(..., description="Email of the cultivar")
    strain_category: StrainCategoryEnum = Field(
        StrainCategoryEnum.HYBRID, description="The category for the flower strain. ex: indica, hybrid, etc."
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
    description_text: Annotated[str, StringConstraints(max_length=500)] = Field(
        "Coming Soon", description="Description of the flower, max 1500 characters"
    )
    effects: Annotated[str, StringConstraints(max_length=500)] = Field(
        "Coming Soon", description="Effects of the flower, max 1500 characters"
    )
    lineage: Annotated[str, StringConstraints(max_length=500)] = Field(
        "Coming Soon", description="Lineage of the flower, max 1500 characters"
    )
    terpenes_list: Optional[List[str]] = Field(None, description="List of terpenes in the flower")
    cultivar: EmailStr = Field(..., description="Email of the cultivar")
    strain_category: StrainCategoryEnum = Field(
        StrainCategoryEnum.HYBRID, description="The category for the flower strain. ex: indica, hybrid, etc."
    )

    @validator("cultivator", "strain", pre=True, always=True)
    def verify_string_and_capitalize_name(cls, v):
        return v.capitalize() if isinstance(v, str) else None


class FlowerVoteCreate(BaseModel):
    cultivator_selected: str = Field(..., description="Selected cultivator's name")
    strain_selected: str = Field(..., description="Selected strain's name")
    structure_vote: confloat(ge=0, le=10.1) = Field(..., description="Vote for the structure of the flower")
    structure_explanation: Annotated[str, StringConstraints(max_length=500)] = Field(
        ..., description="Explanation for the structure vote"
    )
    nose_vote: confloat(ge=0, le=10.1) = Field(
        ..., description="Vote for the nose/fragrance of the flower, from 0 to 10"
    )
    nose_explanation: Annotated[str, StringConstraints(max_length=500)] = Field(
        ..., description="Explanation for the nose vote"
    )
    flavor_vote: confloat(ge=0.0, le=10.1) = Field(..., description="Vote for the flavor of the flower, from 0 to 10")
    flavor_explanation: Annotated[str, StringConstraints(max_length=500)] = Field(
        ..., description="Explanation for the flavor vote"
    )
    effects_vote: confloat(ge=00, le=10.1) = Field(..., description="Vote for the effects of the flower, from 0 to 10")
    effects_explanation: Annotated[str, StringConstraints(max_length=500)] = Field(
        ..., description="Explanation for the effects vote"
    )
    user_email: EmailStr = Field(..., description="Email address of the connoisseur")

    class Config:
        from_attributes = True
        strip_whitespace = True
        populate_by_name = True
        exclude_unset = True


class FlowerVoteResponse(BaseModel):
    cultivator_selected: str = Field(..., description="Selected cultivator's name")
    strain_selected: str = Field(..., description="Selected strain's name")
    structure_vote: confloat(ge=0.0, le=10.1) = Field(..., description="Vote for the structure of the flower")
    structure_explanation: Annotated[str, StringConstraints(max_length=500)] = Field(
        ..., description="Explanation for the structure vote"
    )
    nose_vote: confloat(ge=0, le=10) = Field(
        ..., description="Vote for the nose/fragrance of the flower, from 0 to 10"
    )
    nose_explanation: Annotated[str, StringConstraints(max_length=500)] = Field(
        ..., description="Explanation for the nose vote"
    )
    flavor_vote: confloat(ge=0.0, le=10.1) = Field(..., description="Vote for the flavor of the flower, from 0 to 10")
    flavor_explanation: Annotated[str, StringConstraints(max_length=500)] = Field(
        ..., description="Explanation for the flavor vote"
    )
    effects_vote: confloat(ge=00, le=10.1) = Field(..., description="Vote for the effects of the flower, from 0 to 10")
    effects_explanation: Annotated[str, StringConstraints(max_length=500)] = Field(
        ..., description="Explanation for the effects vote"
    )

    class Config:
        from_attributes = True
        strip_whitespace = True
        populate_by_name = True
        exclude_unset = True


class FlowerRankingBase(BaseModel):
    strain: str
    appearance_rating: float = Field(..., gt=0, lt=10.1)
    freshness_rating: float = Field(..., gt=0, lt=10.1)
    smell_rating: float = Field(..., gt=0, lt=10.1)
    flavor_rating: float = Field(..., gt=0, lt=10.1)
    harshness_rating: float = Field(..., gt=0, lt=10.1)
    effects_rating: float = Field(..., gt=0, lt=10.1)
    appearance_explanation: Optional[str] = Field(None, max_length=500)
    freshness_explanation: Optional[str] = Field(None, max_length=500)
    flavor_explanation: Optional[str] = Field(None, max_length=500)
    smell_explanation: Optional[str] = Field(None, max_length=500)
    harshness_explanation: Optional[str] = Field(None, max_length=500)
    effects_explanation: Optional[str] = Field(None, max_length=500)

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


class CreateHiddenFlowerRanking(CreateFlowerRanking):
    pass


class GetFlowerRanking(CreateFlowerRanking):
    class Config:
        from_attributes = True
        populate_by_name = True


class CreateMysteryFlowerReview(BaseModel):
    cultivator: str = Field(..., description="Name of the cultivator")
    strain: str = Field(..., description="Name of the strain")
    voter_email: EmailStr = Field(..., description="Email address of the voter")
    method_of_consumption: str = Field(..., description="Method used to consume the flower")
    mystery_size_vote: int = Field(..., description="Vote for the mystery size")
    mystery_size_explanation: Optional[str] = Field(None, description="Explanation for the mystery size vote")
    mystery_structure_vote: int = Field(..., description="Vote for the mystery structure")
    mystery_structure_explanation: Optional[str] = Field(
        None, description="Explanation for the mystery structure vote"
    )
    mystery_smell_vote: int = Field(..., description="Vote for the mystery smell")
    mystery_smell_explanation: Optional[str] = Field(None, description="Explanation for the mystery smell vote")
    mystery_freshness_vote: int = Field(..., description="Vote for the mystery freshness")
    mystery_freshness_explanation: Optional[str] = Field(
        None, description="Explanation for the mystery freshness vote"
    )
    mystery_flavor_vote: int = Field(..., description="Vote for the mystery flavor")
    mystery_flavor_explanation: Optional[str] = Field(None, description="Explanation for the mystery flavor vote")
    mystery_effects_vote: int = Field(..., description="Vote for the mystery effects")
    mystery_effects_explanation: Optional[str] = Field(None, description="Explanation for the mystery effects vote")
    mystery_smoothness_vote: int = Field(..., description="Vote for the mystery smoothness")
    mystery_smoothness_explanation: Optional[str] = Field(
        None, description="Explanation for the mystery smoothness vote"
    )

    class Config:
        from_attributes = True
        populate_by_name = True


class FlowerReviewResponse(BaseModel):
    id: int
    strain: StrainType
    cultivator: StrainType
    overall: RatingType
    structure: RatingType
    nose: RatingType
    flavor: RatingType
    effects: RatingType
    card_path: bytes

    class Config:
        from_attributes = True
        populate_by_name = True


class FlowerRankingValuesSchema(BaseModel):
    id: int
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


class FlowerErrorResponse(BaseModel):
    strain: StrainType
    message: str

    class Config:
        from_attributes = True
        populate_by_name = True
