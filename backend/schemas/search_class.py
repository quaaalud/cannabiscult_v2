#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 22 20:12:30 2023

@author: dale
"""

from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional, Union


class SearchResultItem(BaseModel):
    cultivator: str = Field(..., description="Name of the cultivator")
    strain: str = Field(..., description="Name of the strain")
    type: str = Field(..., description="Type of the product")
    url_path: Union[HttpUrl, str] = Field(
        ..., description="URL path to the product details"
    )

    class Config:
        from_attributes = True


class SearchResults(BaseModel):
    results: List[SearchResultItem] = Field(
        ..., description="List of search result items"
    )


class StrainCultivator(BaseModel):
    strain: str
    cultivator: str


class RatingModel(BaseModel):
    product_type: str
    strain: str
    cultivator: str
    appearance_rating: Optional[float] = Field(..., gt=-1, lt=11)
    smell_rating: Optional[float] = Field(..., gt=-1, lt=11)
    freshness_rating: Optional[float] = Field(..., gt=-1, lt=11)
    flavor_rating: Optional[float] = Field(..., gt=-1, lt=11)
    harshness_rating: Optional[float] = Field(..., gt=-1, lt=11)
    effects_rating: Optional[float] = Field(..., gt=-1, lt=11)
    cult_rating: Optional[float] = Field(..., gt=-1, lt=11)

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "product_type": "Flower",
                "strain": "Missouri Belle",
                "cultivator": "Mo Dank",
                "appearance_rating": 7.67,
                "smell_rating": 8.67,
                "freshness_rating": 8.33,
                "flavor_rating": 8.67,
                "harshness_rating": 8.33,
                "effects_rating": 8,
                "cult_rating": 8.28,
            }
        }


class CombinedTerpProfileBaseSchema(BaseModel):
    cultivator: str
    strain: str
    card_path: str
    is_mystery: bool
    voting_open: bool
    product_type: str
    alpha_bergamotene: Optional[float] = Field(..., gt=-1, lt=20)
    alpha_beta_cis_ocimene: Optional[float] = Field(..., gt=-1, lt=20)
    alpha_beta_pinene: Optional[float] = Field(..., gt=-1, lt=20)
    alpha_beta_thujene: Optional[float] = Field(..., gt=-1, lt=20)
    alpha_bisabolene: Optional[float] = Field(..., gt=-1, lt=20)
    alpha_bisabolol: Optional[float] = Field(..., gt=-1, lt=20)
    alpha_cedrene: Optional[float] = Field(..., gt=-1, lt=20)
    alpha_fenchene: Optional[float] = Field(..., gt=-1, lt=20)
    alpha_humulene: Optional[float] = Field(..., gt=-1, lt=20)
    alpha_humulene_epoxide_i: Optional[float] = Field(..., gt=-1, lt=20)
    alpha_phellandrene: Optional[float] = Field(..., gt=-1, lt=20)
    alpha_pinene: Optional[float] = Field(..., gt=-1, lt=20)
    alpha_terpinene: Optional[float] = Field(..., gt=-1, lt=20)
    alpha_terpineol: Optional[float] = Field(..., gt=-1, lt=20)
    alpha_terpinolene: Optional[float] = Field(..., gt=-1, lt=20)
    alpha_thujene: Optional[float] = Field(..., gt=-1, lt=20)
    alpha_zingiberene: Optional[float] = Field(..., gt=-1, lt=20)
    beta_asarone: Optional[float] = Field(..., gt=-1, lt=20)
    beta_bisabolene: Optional[float] = Field(..., gt=-1, lt=20)
    beta_caryophyllene_oxide: Optional[float] = Field(..., gt=-1, lt=20)
    beta_farnesene: Optional[float] = Field(..., gt=-1, lt=20)
    beta_myrcene: Optional[float] = Field(..., gt=-1, lt=20)
    beta_ocimene: Optional[float] = Field(..., gt=-1, lt=20)
    beta_pinene: Optional[float] = Field(..., gt=-1, lt=20)
    beta_selinene: Optional[float] = Field(..., gt=-1, lt=20)
    beta_terpinene: Optional[float] = Field(..., gt=-1, lt=20)
    camphene: Optional[float] = Field(..., gt=-1, lt=20)
    caryophyllene: Optional[float] = Field(..., gt=-1, lt=20)
    caryophyllene_oxide: Optional[float] = Field(..., gt=-1, lt=20)
    cis_nerolidol: Optional[float] = Field(..., gt=-1, lt=20)
    cis_beta_ocimene: Optional[float] = Field(..., gt=-1, lt=20)
    delta_3_carene: Optional[float] = Field(..., gt=-1, lt=20)
    delta_limonene: Optional[float] = Field(..., gt=-1, lt=20)
    eucalyptol: Optional[float] = Field(..., gt=-1, lt=20)
    gamma_terpinene: Optional[float] = Field(..., gt=-1, lt=20)
    geraniol: Optional[float] = Field(..., gt=-1, lt=20)
    guaiol: Optional[float] = Field(..., gt=-1, lt=20)
    isoborneol: Optional[float] = Field(..., gt=-1, lt=20)
    isopulegol: Optional[float] = Field(..., gt=-1, lt=20)
    limonene: Optional[float] = Field(..., gt=-1, lt=20)
    linalool: Optional[float] = Field(..., gt=-1, lt=20)
    myrcene: Optional[float] = Field(..., gt=-1, lt=20)
    nerolidol: Optional[float] = Field(..., gt=-1, lt=20)
    ocimene: Optional[float] = Field(..., gt=-1, lt=20)
    p_cymene: Optional[float] = Field(..., gt=-1, lt=20)
    para_cymene: Optional[float] = Field(..., gt=-1, lt=20)
    phellandrene: Optional[float] = Field(..., gt=-1, lt=20)
    terpineol: Optional[float] = Field(..., gt=-1, lt=20)
    terpinolene: Optional[float] = Field(..., gt=-1, lt=20)
    trans_nerolidol: Optional[float] = Field(..., gt=-1, lt=20)
    trans_ocimene: Optional[float] = Field(..., gt=-1, lt=20)
    y_terpinene: Optional[float] = Field(..., gt=-1, lt=20)
    beta_caryophyllene: Optional[float] = Field(..., gt=-1, lt=20)

    class Config:
        from_attributes = True
        exclude_unset_fields = True


class FlowerTerpTableSchema(CombinedTerpProfileBaseSchema):
    flower_id: int


class ConcentrateTerpTableSchema(CombinedTerpProfileBaseSchema):
    concentrate_id: int


class PreRollTerpTableSchema(CombinedTerpProfileBaseSchema):
    pre_roll_id: int


class EdibleTerpTableSchema(CombinedTerpProfileBaseSchema):
    edible_id: int
