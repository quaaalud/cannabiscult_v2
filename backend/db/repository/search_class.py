#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 22 20:12:12 2023

@author: dale
"""

from typing import Type, List, Dict, Any
import traceback
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.future import select
from db.base import Base
from db.models.flowers import Flower
from db.models.concentrates import Concentrate
from db.models.edibles import Edible
from db._supabase.connect_to_storage import return_image_url_from_supa_storage


async def get_data_by_strain(
    db: AsyncSession, model: Type[Base], strain: str
) -> List[Dict[str, Any]]:
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


async def search_strain(db: AsyncSession, strain: str) -> List[Dict[str, Any]]:
    flower_results = await get_data_by_strain(db, Flower, strain)
    concentrate_results = await get_data_by_strain(db, Concentrate, strain)
    try:
        edible_results = await get_data_by_strain(db, Edible, strain)
    except ProgrammingError:
        edible_results = []

    return flower_results + concentrate_results + edible_results
