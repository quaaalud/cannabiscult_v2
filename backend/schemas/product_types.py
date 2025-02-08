#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov  5 16:47:38 2023

@author: dale
"""

import enum
from fastapi import Form
from pydantic import BaseModel, Json, Field, EmailStr, field_validator
from typing import Optional, Annotated, List


class ProductTypes(BaseModel):
    product_type: str = Field(..., description="Type of the product")
    extra_data: Optional[Json] = Field(None, description="Additional data in JSON format, optional")

    class Config:
        from_attributes = True
        exclude_unset = True
        populate_by_name = True
        strip_whitespace = True


class StrainCategoryEnum(str, enum.Enum):
    INDICA = "indica"
    INDICA_HYBRID = "indica_dominant_hybrid"
    HYBRID = "hybrid"
    SATICA_HYBRID = "sativa_dominant_hybrid"
    SATIVA = "sativa"
    CULT_PACK = "cult_pack"


class ProductSubmission(ProductTypes):
    strain: Annotated[str, Field(min_length=1, max_length=100, description="Name of the strain")]
    cultivator: Annotated[str, Field(min_length=1, max_length=100, description="Name of the cultivator")]
    cultivar_email: EmailStr = Field(..., description="Email address of the cultivar")
    description: Annotated[str, Field(max_length=500, description="Detailed description for the product")] = (
        "Coming Soon!"
    )
    effects: Annotated[str, Field(max_length=500, description="Effects details for the product")] = "Coming Soon!"
    lineage: Annotated[str, Field(max_length=500, description="Lineage or ancestry information")] = "Coming Soon!"
    terpenes_list: List[Annotated[str, Field(max_length=50, description="Name of a terpene")]] = ["Coming", "Soon!"]
    strain_category: StrainCategoryEnum = Field(StrainCategoryEnum.HYBRID, description="Category of the strain")

    @field_validator("strain", "cultivator", mode="before")
    @classmethod
    def strip_whitespace_from_names(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("This field cannot be empty.")
        return v.strip()

    @field_validator("description", "effects", "lineage", mode="before")
    @classmethod
    def set_default_if_empty(cls, v: str, info):
        if v is None or not v.strip():
            return info.default
        return v.strip()

    @classmethod
    def as_form(
        cls,
        product_type: str = Form(...),
        strain: str = Form(...),
        cultivator: str = Form(...),
        cultivar_email: EmailStr = Form(...),
        description: str = Form("Coming Soon!"),
        effects: str = Form("Coming Soon!"),
        lineage: str = Form("Coming Soon!"),
        terpenes_list: List[str] = Form(["Coming", "Soon!"]),
        strain_category: StrainCategoryEnum = Form(StrainCategoryEnum.HYBRID),
        extra_data: Optional[str] = Form(None),
    ) -> "ProductSubmission":
        return cls(
            product_type=product_type,
            strain=strain,
            cultivator=cultivator,
            cultivar_email=cultivar_email,
            description=description,
            effects=effects,
            lineage=lineage,
            terpenes_list=terpenes_list,
            strain_category=strain_category,
            extra_data=extra_data,
        )

    class Config:
        from_attributes = True
        exclude_unset = True
        populate_by_name = True
        strip_whitespace = True
        extra = "forbid"
