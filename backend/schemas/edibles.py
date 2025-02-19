#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 30 22:04:15 2023

@author: dale
"""

from typing import Optional, Annotated
from pydantic import BaseModel, EmailStr, Field, confloat, StringConstraints, validator
from schemas.product_types import StrainCategoryEnum, StrainType


class EdiblesBase(BaseModel):
    cultivator: Annotated[str, StringConstraints(max_length=1500)] = Field(..., description="Name of the cultivator")
    strain: Annotated[str, StringConstraints(max_length=1500)] = Field(..., description="Name of the strain")
    card_path: Annotated[str, StringConstraints(max_length=1500)] = Field(
        ..., description="Path to the edible's image card"
    )
    product_type: str = Field("edible", description="The category for the flower strain. ex: indica, hybrid, etc.")

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


class Edible(EdiblesBase):
    pass


class MysteryEdibleBase(EdiblesBase):
    pass


class Vibe_Edible_Base(EdiblesBase):
    pass


class Get_Vibe_Edible(Vibe_Edible_Base):
    pass


class EdibleRankingBase(BaseModel):
    strain: Annotated[str, StringConstraints(max_length=500)]
    appearance_rating: confloat = Field(..., gt=0, lt=10.1)
    flavor_rating: confloat = Field(..., gt=0, lt=10.1)
    aftertaste_rating: confloat = Field(..., gt=0, lt=10.1)
    effects_rating: confloat = Field(..., gt=0, lt=10.1)
    appearance_explanation: Optional[Annotated[str, StringConstraints(max_length=1500)]] = Field(None, max_length=1500)
    flavor_explanation: Optional[Annotated[str, StringConstraints(max_length=1500)]] = Field(None, max_length=1500)
    aftertaste_explanation: Optional[Annotated[str, StringConstraints(max_length=1500)]] = Field(None, max_length=1500)
    effects_explanation: Optional[Annotated[str, StringConstraints(max_length=1500)]] = Field(None, max_length=1500)


class GetEdibleRanking(BaseModel):
    edible_id: int = Field(...)
    connoisseur: EmailStr = Field(...)
    cultivator: Optional[Annotated[str, StringConstraints(max_length=500)]] = Field(None, max_length=199)
    strain: Annotated[str, StringConstraints(max_length=500)] = Field(..., max_length=200)
    flavor: Annotated[str, StringConstraints(max_length=500)] = Field(..., max_length=200)

    appearance_rating: confloat = Field(..., gt=0, lt=10.1)
    flavor_rating: confloat = Field(..., gt=0, lt=10.1)
    feel_rating: confloat = Field(..., gt=0, lt=10.1)
    chew_rating: confloat = Field(..., gt=0, lt=10.1)
    effects_rating: confloat = Field(..., gt=0, lt=10.1)
    appearance_explanation: Optional[Annotated[str, StringConstraints(max_length=1500)]] = Field(None, max_length=1500)
    flavor_explanation: Optional[Annotated[str, StringConstraints(max_length=1500)]] = Field(None, max_length=1500)
    feel_explanation: Optional[Annotated[str, StringConstraints(max_length=1500)]] = Field(None, max_length=1500)
    chew_explanation: Optional[Annotated[str, StringConstraints(max_length=1500)]] = Field(None, max_length=1500)
    effects_explanation: Optional[Annotated[str, StringConstraints(max_length=1500)]] = Field(None, max_length=1500)

    class Config:
        from_attributes = True


class CreateEdibleRanking(BaseModel):
    edible_id: int = Field(...)
    connoisseur: EmailStr = Field(...)
    cultivator: Optional[Annotated[str, StringConstraints(max_length=500)]] = Field(None, max_length=199)
    strain: Annotated[str, StringConstraints(max_length=500)] = Field(..., max_length=200)

    appearance_rating: float = Field(..., gt=0, lt=10.1)
    aftertaste_rating: float = Field(..., gt=0, lt=10.1)
    flavor_rating: float = Field(..., gt=0, lt=10.1)
    feel_rating: float = Field(..., gt=0, lt=10.1)
    chew_rating: float = Field(..., gt=0, lt=10.1)
    effects_rating: float = Field(..., gt=0, lt=10.1)
    appearance_explanation: Optional[Annotated[str, StringConstraints(max_length=1500)]] = Field(None, max_length=1500)
    flavor_explanation: Optional[Annotated[str, StringConstraints(max_length=1500)]] = Field(None, max_length=1500)
    feel_explanation: Optional[Annotated[str, StringConstraints(max_length=1500)]] = Field(None, max_length=1500)
    chew_explanation: Optional[Annotated[str, StringConstraints(max_length=1500)]] = Field(None, max_length=1500)
    aftertaste_explanation: Optional[Annotated[str, StringConstraints(max_length=1500)]] = Field(None, max_length=1500)
    effects_explanation: Optional[Annotated[str, StringConstraints(max_length=1500)]] = Field(None, max_length=1500)

    class Config:
        from_attributes = True
        populate_by_name = True
        exclude_unset = True
        strip_whitespace = True


class GetVibeEdibleRanking(GetEdibleRanking):
    pass


class CreateVibeEdibleRanking(CreateEdibleRanking):
    pass


class EdibleDescriptionBase(BaseModel):
    edible_id: int = Field(None, description="Unique identifier for the edible")
    description: Annotated[str, StringConstraints(max_length=1500)] = Field(
        "Coming Soon", description="Description of the edible, max 1500 characters"
    )
    effects: Annotated[str, StringConstraints(max_length=1500)] = Field(
        "Coming Soon", description="Effects of the edible, max 1500 characters"
    )
    lineage: Annotated[str, StringConstraints(max_length=1500)] = Field(
        "Coming Soon", description="Lineage of the edible, max 1500 characters"
    )
    cultivar_email: EmailStr = Field(..., description="Email of the cultivar")
    strain_category: StrainCategoryEnum = Field(
        StrainCategoryEnum.cult_pack, description="The category for the edible strain. ex: indica, hybrid, etc."
    )

    class Config:
        from_attributes = True
        use_enum_values = True
        strip_whitespace = True
        exclude_unset = True


class AddEdibleDescription(EdibleDescriptionBase):
    pass


class GetEdibleWithDescription(BaseModel):
    edible_id: int = Field(..., description="Unique identifier for the edible")
    cultivator: StrainType = Field(..., description="Name of the cultivator")
    strain: StrainType = Field(..., description="Name of the strain")
    is_mystery: bool = Field(..., description="Indicates if the edible is a mystery")
    url_path: str = Field(..., description="Path to the edible's image card")
    voting_open: bool = Field(True, description="Indicates if voting is open for this edible")
    product_type: str = Field("edible", description="Type of the product, default is 'edible'")

    description_id: int = Field(..., description="Unique identifier for the edible description")
    description_text: Annotated[str, StringConstraints(max_length=1500)] = Field(
        "Coming Soon", description="Description of the edible, max 1500 characters"
    )
    effects: Annotated[str, StringConstraints(max_length=1500)] = Field(
        "Coming Soon", description="Effects of the edible, max 1500 characters"
    )
    lineage: Annotated[str, StringConstraints(max_length=1500)] = Field(
        "Coming Soon", description="Lineage of the flower, max 1500 characters"
    )
    cultivar: EmailStr = Field(..., description="Email of the cultivar")
    strain_category: StrainCategoryEnum = Field(
        StrainCategoryEnum.cult_pack, description="The category for the edible strain. ex: indica, hybrid, etc."
    )

    class Config:
        from_attributes = True
        use_enum_values = True
        strip_whitespace = True
        exclude_unset = True
