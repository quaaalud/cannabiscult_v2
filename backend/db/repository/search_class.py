#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 22 20:12:12 2023

@author: dale
"""

import random
import traceback
from typing import Type, List, Dict, Any, Optional, Union
from sqlalchemy import inspect, func, or_, not_, union_all
from sqlalchemy.orm import Session
from sqlalchemy.exc import ProgrammingError, SQLAlchemyError
from sqlalchemy.future import select
from db.base import Base
from schemas.search_class import (
    RatingModel,
    FlowerTerpTableSchema,
    ConcentrateTerpTableSchema,
    EdibleTerpTableSchema,
    PreRollTerpTableSchema,
)
from core.config import settings
from db.models.flowers import Flower
from db.models.concentrates import Concentrate
from db.models.edibles import Edible, VibeEdible
from db.models.pre_rolls import Pre_Roll
from db.models.product_types import (
    Product_Types,
    FlowerTerpTable,
    ConcentrateTerpTable,
    EdibleTerpTable,
    PreRollTerpTable,
)
from db.models.calendar_events import (
    CalendarEvent,
    CalendarEventQuery,
    SimpleProductSchema,
)
from db._supabase.connect_to_storage import return_image_url_from_supa_storage


async def get_data_by_strain(
    db: Session, model: Type[Base], strain: str
) -> List[Dict[str, Any]]:
    if model == VibeEdible:
        return []
    try:
        result = db.execute(
            select(model)
            .filter(model.cultivator != "Cultivar")
            .filter(model.cultivator != "Connoisseur")
            .filter(model.strain.ilike(f"%{strain}%"))
            .filter(model.strain.ilike("%Test%") == False)
        )
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
        general_edibles = await get_data_by_strain(db, Edible, strain)
    except ProgrammingError:
        general_edibles = []
    vibe_edibles = await get_data_by_strain(db, VibeEdible, strain)
    for item in vibe_edibles:
        item["type"] = "Edible"
    edible_results = [*general_edibles, *vibe_edibles]
    pre_roll_results = await get_data_by_strain(db, Pre_Roll, strain)
    return flower_results + concentrate_results + edible_results + pre_roll_results


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
        result = db.execute(
            select(model.cultivator)
            .filter(model.cultivator != "Cultivar")
            .filter(model.cultivator != "Connoisseur")
            .distinct()
        )
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
        result = db.execute(
            select(model.strain)
            .where(model.cultivator == cultivator)
            .filter(model.cultivator != "Cultivar")
            .filter(model.cultivator != "Connoisseur")
            .filter(model.strain.ilike("%Test%") == False)
        )
        strains = result.scalars().all()
        return [strain for strain in strains if "test" not in strain.lower()]
    except Exception as e:
        traceback.print_exc()
        print(
            f"Error fetching strains for {model.__name__} and cultivator {cultivator}: {e}"
        )
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


@settings.retry_db
async def aggregate_ratings_by_strain(db: Session, model_dict: dict) -> List[RatingModel]:
    all_ratings = []
    for product_type, models in model_dict.items():
        for model in models:
            # Get all column names from the model, focusing on those ending with "_rating"
            columns = [c.name for c in inspect(model).c]
            rating_columns = [col for col in columns if col.endswith("_rating")]
            # Build dynamic selection of columns for aggregation, excluding None values
            selection = [model.strain, model.cultivator] + [
                func.avg(func.nullif(getattr(model, col), None)).label(col)
                for col in rating_columns
            ]
            # Execute query to aggregate ratings, applying the specified filters
            query = (
                db.query(*selection)
                .filter(
                    model.cultivator != "Cultivar",
                    model.cultivator != "Connoisseur",
                    not_(
                        model.strain.ilike("%Test%")
                    ),  # Excluding strains that contain 'Test'
                    or_(*[getattr(model, col) != None for col in rating_columns]),
                )
                .group_by(model.strain, model.cultivator)
            )
            ratings = query.all()
            # Convert and accumulate results
            for rating in ratings:
                rating_data = {
                    "product_type": product_type,
                    "strain": rating.strain,
                    "cultivator": rating.cultivator,
                }
                # Compute the overall average rating
                sum_ratings = 0
                count_ratings = 0
                for col in rating_columns:
                    rating_value = getattr(rating, col)
                    if rating_value is not None:
                        rounded_rating = round(float(rating_value), 2)
                        rating_data[col] = rounded_rating
                        sum_ratings += rounded_rating
                        count_ratings += 1
                # Calculate the 'cult_rating'
                if count_ratings > 0:
                    rating_data["cult_rating"] = round(sum_ratings / count_ratings, 2)
                else:
                    rating_data["cult_rating"] = None
                all_ratings.append(rating_data)
    return all_ratings


def get_all_card_paths(db: Session, limit=10) -> List[dict]:
    # Prepare select statements for each product type
    select_flower = select(
        Flower.cultivator, Flower.strain, Flower.card_path, Flower.product_type
    ).filter(Flower.strain.notilike("%Test%"), Flower.cultivator != "Connoisseur")
    select_concentrate = select(
        Concentrate.cultivator,
        Concentrate.strain,
        Concentrate.card_path,
        Concentrate.product_type,
    ).filter(
        Concentrate.strain.notilike("%Test%"), Concentrate.cultivator != "Connoisseur"
    )
    select_pre_roll = select(
        Pre_Roll.cultivator, Pre_Roll.strain, Pre_Roll.card_path, Pre_Roll.product_type
    ).filter(Pre_Roll.strain.notilike("%Test%"), Pre_Roll.cultivator != "Connoisseur")
    select_edible = select(
        Edible.cultivator, Edible.strain, Edible.card_path, Edible.product_type
    ).filter(Edible.strain.notilike("%Test%"), Edible.cultivator != "Connoisseur")

    # Combine queries using UNION ALL with limit and offset
    combined_query = union_all(
        select_flower, select_concentrate, select_pre_roll, select_edible
    )
    # Create a subquery for counting
    subquery = combined_query.alias("subquery")
    total_rows = db.execute(select(func.count()).select_from(subquery)).scalar()
    if total_rows == 0:
        return []  # Early return if no products
    random_offset = random.randint(0, total_rows - 1)
    # Execute the query
    result = db.execute(combined_query.offset(random_offset).limit(limit)).fetchall()
    additional_needed = int(limit) - len(result)
    if additional_needed > 0:
        # Fetch the remainder from the beginning of the dataset
        result += db.execute(combined_query.limit(additional_needed)).fetchall()
    return [
        {
            "cultivator": row.cultivator,
            "strain": row.strain,
            "card_path": row.card_path,
            "product_type": row.product_type,
        }
        for row in result
    ]


async def generate_signed_urls(product_data: List[dict]):
    yield "[".encode("utf-8")  # Start of JSON array
    first = True
    for product in product_data:
        try:
            signed_url = return_image_url_from_supa_storage(str(product["card_path"]))
            product_info = SimpleProductSchema(
                cultivator=product["cultivator"],
                strain=product["strain"],
                signed_url=signed_url,
                product_type=product["product_type"],
            ).json()  # Serialize to JSON string
            if not first:
                yield ", ".encode("utf-8")  # Properly format JSON array
            yield product_info.encode("utf-8")
            first = False
        except Exception as e:
            print(f"Failed to generate URL for {product['card_path']}: {e}")
    yield "]".encode("utf-8")  # End of JSON array


async def get_all_events(db: Session) -> List[CalendarEventQuery]:
    try:
        result = db.execute(select(CalendarEvent))
        events = result.scalars().all()
        return [CalendarEventQuery.from_orm(event) for event in events]
    except SQLAlchemyError as e:
        traceback.print_exc()
        print(f"Error fetching all events: {e}")
        return []


async def add_new_calendar_event(db: Session, event_data: dict) -> bool:
    try:
        # Check if an event with the same summary and start date exists
        existing_event = (
            db.execute(
                select(CalendarEvent).filter_by(
                    summary=event_data["summary"], start_date=event_data["start_date"]
                )
            )
            .scalars()
            .first()
        )
        # If the event exists, use update_calendar_event to update it
        if existing_event:
            return await update_calendar_event(
                db, event_data["summary"], event_data["start_date"], event_data
            )
        # If no existing event, create a new one
        new_event = CalendarEvent(**event_data)
        db.add(new_event)
    except SQLAlchemyError as e:
        db.rollback()
        traceback.print_exc()
        print(f"Error adding new event: {e}")
        return False
    else:
        db.commit()
    return True


async def update_calendar_event(
    db: Session, summary: str, start_date: str, new_data: dict
) -> bool:
    try:
        event = (
            db.execute(
                select(CalendarEvent).filter_by(summary=summary, start_date=start_date)
            )
            .scalars()
            .first()
        )
        if not event:
            print("No matching event found for update.")
            return False
        # Update fields that are not None in new_data
        for key, value in new_data.items():
            if value is not None:
                setattr(event, key, value)
        db.commit()
        return True
    except SQLAlchemyError as e:
        db.rollback()
        traceback.print_exc()
        print(f"Error updating event: {e}")
        return False


async def get_card_path_by_details(
    db: Session, product_type: str, strain: str, cultivator: str
) -> Optional[str]:
    # Map product types to their respective model classes
    model_mapping = {
        "Flower": Flower,
        "Concentrate": Concentrate,
        "Edible": Edible,
        "Pre_Roll": Pre_Roll,
        "VibeEdible": VibeEdible,
    }
    # Fetch the correct model based on product_type
    model = model_mapping.get(product_type)
    if model is None:
        return None

    try:
        result = db.execute(
            select(model.card_path)
            .where(
                model.strain == strain,
                model.cultivator == cultivator,
                model.strain.ilike("%Test%") == False,
            )
            .limit(1)
        ).scalar_one()
        return result
    except Exception as e:
        print(f"Error for card_path on {model.__name__}, {strain}, {cultivator}: {e}")
        return None


def get_all_strains_by_product_type(db: Session, product_type: str) -> List[Dict[str, any]]:
    # Mapping of product types to models
    product_mapping = {
        "flower": FlowerTerpTable,
        "concentrate": ConcentrateTerpTable,
        "pre_roll": PreRollTerpTable,
        "edible": EdibleTerpTable,
    }
    model = product_mapping.get(product_type.lower())
    if not model:
        raise ValueError("Invalid product type provided")
    try:
        # Fetch all strains and their primary keys
        primary_key = [key.name for key in inspect(model).primary_key][0]
        data = db.query(getattr(model, primary_key), model.strain).all()
        return [{"product_id": item[0], "strain": item[1]} for item in data]
    except Exception as e:
        print(f"Error fetching strains for {product_type}: {e}")
        return []


def get_terp_profile_by_type(db: Session, product_type: str, product_id: int) -> Union[
    FlowerTerpTableSchema,
    ConcentrateTerpTableSchema,
    EdibleTerpTableSchema,
    PreRollTerpTableSchema,
]:
    # Mapping of product types to models and schemas
    product_mapping = {
        "flower": (FlowerTerpTable, FlowerTerpTableSchema),
        "concentrate": (ConcentrateTerpTable, ConcentrateTerpTableSchema),
        "pre_roll": (PreRollTerpTable, PreRollTerpTableSchema),
        "edible": (EdibleTerpTable, EdibleTerpTableSchema),
    }
    model, schema = product_mapping.get(product_type.lower(), (None, None))
    if not model:
        raise ValueError("Invalid product type provided")
    # Dynamically fetch the primary key column name from the model
    primary_key = [key.name for key in inspect(model).primary_key][0]
    # Fetch the data from the database
    data = db.query(model).filter(getattr(model, primary_key) == product_id).first()
    if data is None:
        return None
    # Serialize data using the corresponding Pydantic schema
    return schema.from_orm(data)
