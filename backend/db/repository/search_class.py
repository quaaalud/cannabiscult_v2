#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 22 20:12:12 2023

@author: dale
"""

from typing import Type, List, Dict, Any, Optional
import traceback
from sqlalchemy.orm import Session
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.sql import func
from sqlalchemy.future import select
from db.base import Base
from db.models.flowers import Flower
from db.models.concentrates import Concentrate
from db.models.edibles import Edible
from db.models.product_types import Product_Types
from db._supabase.connect_to_storage import return_image_url_from_supa_storage


async def get_data_by_strain(db: Session, model: Type[Base], strain: str) -> List[Dict[str, Any]]:
    try:
        result = db.execute(select(model).filter(model.strain.ilike(f"%{strain}%")))
        items = result.scalars().all()
        return [
            {
                "cultivator": item.cultivator,
                "strain": item.strain,
                "type": model.__name__,
                "url_path": return_image_url_from_supa_storage(str(item.card_path)),
            }
            for item in items
        ]
    except Exception as e:
        traceback.print_exc()
        print(f"Error fetching data for {model.__name__}: {e}")
        return []


async def search_strain(db: Session, strain: str) -> List[Dict[str, Any]]:
    flower_results = await get_data_by_strain(db, Flower, strain)
    concentrate_results = await get_data_by_strain(db, Concentrate, strain)
    try:
        edible_results = await get_data_by_strain(db, Edible, strain)
    except ProgrammingError:
        edible_results = []

    return flower_results + concentrate_results + edible_results


async def get_all_product_types(db: Session) -> List[str]:
    try:
        result = db.execute(select(Product_Types.product_type))
        product_types = result.scalars().all()
        return [product_type for product_type in product_types]
    except Exception as e:
        traceback.print_exc()
        print(f"Error fetching product types: {e}")
        return []


def get_cultivators_by_product_type(db: Session, model: Type[Base]) -> List[str]:
    try:
        result = db.execute(select(model.cultivator).distinct())
        cultivators = result.scalars().all()
        return [cultivator for cultivator in cultivators]
    except Exception as e:
        traceback.print_exc()
        print(f"Error fetching cultivators for {model.__name__}: {e}")
        return []


def get_strains_by_cultivator(
    db: Session, model: Type[Base], cultivator: str
) -> Optional[List[str]]:
    try:
        result = db.execute(select(model.strain).where(model.cultivator == cultivator))
        strains = result.scalars().all()
        return [strain for strain in strains if 'test' not in strain.lower()]
    except Exception as e:
        traceback.print_exc()
        print(f"Error fetching strains for {model.__name__} and cultivator {cultivator}: {e}")
        return None


def get_random_cultivator(db: Session, model: Type[Base]) -> str:
    try:
        result = db.execute(
            select(model.cultivator).distinct().order_by(func.random()).limit(1)
        )
        random_cultivator = result.scalar_one()
        return random_cultivator
    except Exception as e:
        traceback.print_exc()
        print(f"Error fetching random cultivator for {model.__name__}: {e}")
        return ""


def get_random_strain(db: Session, model: Type[Base]) -> str:
    try:
        result = db.execute(
            select(model.strain).distinct().order_by(func.random()).limit(1)
        )
        random_strain = result.scalar_one()
        return random_strain
    except Exception as e:
        traceback.print_exc()
        print(f"Error fetching random strain for {model.__name__}: {e}")
        return ""
