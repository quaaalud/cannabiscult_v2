#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov  5 16:47:38 2023

@author: dale
"""

import json
import enum
from typing import Optional, Annotated, List, Any, Dict, Type
from sqlalchemy.inspection import inspect
from fastapi import Form
from pydantic import (
    BaseModel,
    Json,
    Field,
    EmailStr,
    field_validator,
    StringConstraints,
    create_model,
    ValidationError,
)

StrainType = Annotated[str, Annotated[str, StringConstraints(min_length=1, max_length=500)]]


base_fields = {
    "product_type": (StrainType, ...),
    "strain": (StrainType, ...),
    "cultivator": (StrainType, ...),
    "cult_rating": (Optional[float], None),
}


def create_rating_schema(model: Type) -> Type[BaseModel]:
    columns = inspect(model).c
    rating_fields = {
        col.name: (Optional[float], Field(None, gt=-1, lt=11)) for col in columns if col.name.endswith("_rating")
    }
    all_fields = {**base_fields, **rating_fields}
    schema_name = f"{model.__name__}RatingSchema"
    return create_model(schema_name, **all_fields)


class StrainCategoryEnum(str, enum.Enum):
    indica = "indica"
    indica_dominant_hybrid = "indica_dominant_hybrid"
    hybrid = "hybrid"
    sativa_dominant_hybrid = "sativa_dominant_hybrid"
    sativa = "sativa"
    cult_pack = "cult_pack"


class RatingsErrorResponse(BaseModel):
    strain: StrainType
    message: str

    class Config:
        from_attributes = True
        populate_by_name = True


class ProductTypes(BaseModel):
    product_type: str = Field(..., description="Type of the product")
    extra_data: Optional[Json] = Field(None, description="Additional data in JSON format, optional")

    class Config:
        from_attributes = True
        exclude_unset = True
        populate_by_name = True
        strip_whitespace = True


class ProductSubmission(ProductTypes):
    strain: Annotated[str, Field(min_length=1, max_length=100, description="Name of the strain")]
    cultivator: Annotated[str, Field(min_length=1, max_length=100, description="Name of the cultivator")]
    cultivar_email: EmailStr = Field(..., description="Email address of the cultivar")
    description: Annotated[str, Field(max_length=1500, description="Detailed description for the product")] = (
        "Coming Soon!"
    )
    effects: Annotated[str, Field(max_length=1500, description="Effects details for the product")] = "Coming Soon!"
    lineage: Annotated[str, Field(max_length=1500, description="Lineage or ancestry information")] = "Coming Soon!"
    terpenes_list: List[Annotated[str, Field(max_length=1500, description="Name of a terpene")]] = ["Coming", "Soon!"]
    strain_category: StrainCategoryEnum = Field(StrainCategoryEnum.cult_pack, description="Category of the strain")
    terpenes_map: Dict[str, float] = Field(default_factory={})

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

    @field_validator("strain_category", mode="before")
    @classmethod
    def convert_strain_category(cls, v: Any) -> StrainCategoryEnum:
        """
        This validator ensures that the strain_category field will be converted to a
        StrainCategoryEnum member even if a raw string is provided.
        """
        if isinstance(v, str):
            try:
                return StrainCategoryEnum(v)
            except ValueError:
                # Optional: try a case-insensitive match if needed
                v_lower = v.lower()
                for member in StrainCategoryEnum:
                    if member.value.lower() == v_lower:
                        return member
                raise ValueError(f"Invalid strain_category: {v}")
        elif isinstance(v, StrainCategoryEnum):
            return v
        else:
            raise ValueError(f"Invalid type for strain_category: {type(v)}")

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
        strain_category: StrainCategoryEnum = Form(StrainCategoryEnum.cult_pack),
        terpenes_map: Optional[str] = Form(None),
        extra_data: Optional[str] = Form(None),
    ) -> "ProductSubmission":
        if terpenes_map:
            parsed_terps = json.loads(terpenes_map)
        else:
            parsed_terps = {}
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
            terpenes_map=parsed_terps,
        )

    class Config:
        from_attributes = True
        exclude_unset = True
        populate_by_name = True
        strip_whitespace = True
        extra = "forbid"


class AggregatedStrainRatingSchema(BaseModel):
    product_type: str = Field(..., min_length=1, max_length=50)
    strain: str = Field(..., min_length=1, max_length=500)
    cultivator: str = Field(..., min_length=1, max_length=500)
    cult_rating: float | None = Field(None, ge=0, le=10)
    ratings: dict[str, float | None]

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "product_type": "Concentrate",
                "strain": "Guava Tart",
                "cultivator": "Vibe",
                "cult_rating": 8.54,
                "ratings": {
                    "color_rating": 8.21,
                    "flavor_rating": 8.08,
                    "effects_rating": 8.33,
                    "consistency_rating": 8.75,
                    "residuals_rating": 8.00,
                    "smell_rating": 8.50,
                },
            }
        }


def convert_to_aggregated_rating_schema(data: List[Dict[str, Any]]) -> List[AggregatedStrainRatingSchema]:
    converted_ratings = []
    for item in data:
        base_data = {
            "product_type": item.get("product_type", ""),
            "strain": item.get("strain", ""),
            "cultivator": item.get("cultivator", ""),
            "cult_rating": item.get("cult_rating"),
        }
        ratings = {key: value for key, value in item.items() if key.endswith("_rating") and key != "cult_rating"}
        base_data["ratings"] = ratings

        try:
            validated_schema = AggregatedStrainRatingSchema(**base_data)
            converted_ratings.append(validated_schema)
        except ValidationError as e:
            print(f"Validation error for {base_data['strain']} - {base_data['cultivator']}: {e}")
            pass
    return converted_ratings
