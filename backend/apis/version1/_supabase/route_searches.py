#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 22 20:27:46 2023

@author: dale
"""

import base64
import random
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from fastapi.responses import StreamingResponse
from sqlalchemy import not_
from sqlalchemy.orm import Session
from uuid import uuid4
from db.session import get_db
from typing import List, Optional, Any, Dict, Union
from schemas.flowers import GetFlowerRanking
from schemas.concentrates import GetConcentrateRanking
from schemas.pre_rolls import GetPreRollRanking
from schemas.edibles import GetVibeEdibleRanking
from db.base import (
    Flower,
    Flower_Ranking,
    Concentrate,
    Edible,
    VibeEdible,
    Pre_Roll,
    Pre_Roll_Ranking,
    Concentrate_Ranking,
    Vibe_Edible_Ranking,
    CalendarEventQuery,
    User,
)
from db.repository.search_class import (
    search_strain,
    get_all_product_types,
    get_cultivators_by_product_type,
    get_strains_by_cultivator,
    get_strains_for_moluv_collab,
    get_random_cultivator,
    aggregate_ratings_by_strain,
    get_all_card_paths,
    generate_signed_urls,
    get_all_events,
    add_new_calendar_event,
    get_all_strains_by_product_type,
    get_terp_profile_by_type,
    build_strains_family_tree_graph,
    get_product_with_terp_profile,
    serialize_graph,
    get_user_ranking_for_product,
)
from schemas.search_class import (
    SearchResultItem,
    StrainCultivator,
    FlowerTerpTableSchema,
    ConcentrateTerpTableSchema,
    EdibleTerpTableSchema,
    PreRollTerpTableSchema,
    ProductWithTerpProfileSchema,
)
from core.config import settings

tasks = {}

router = APIRouter()


product_type_to_model = {
    "Flower": [Flower],
    "Concentrate": [Concentrate],
    "Edible": [Edible, VibeEdible],
    "Pre-Roll": [Pre_Roll],
    # Add other product types here
}


product_type_to_ranking_model = {
    "Flower": [Flower_Ranking],
    "Concentrate": [Concentrate_Ranking],
    "Edible": [Vibe_Edible_Ranking],
    "Pre-Roll": [Pre_Roll_Ranking],
    # Add other product types here
}


def convert_to_schema(product_type: str, data: List[dict]):
    schema_map = {
        "Flower": GetFlowerRanking,
        "Concentrate": GetConcentrateRanking,
        "Edible": GetVibeEdibleRanking,
        "Pre-Roll": GetPreRollRanking,
    }
    schema_class = schema_map.get(product_type)
    if not schema_class:
        raise ValueError(f"Unsupported product type: {product_type}")
    return [schema_class(**item) for item in data]


def model_to_dict(model_instance):
    """Converts an SQLAlchemy model instance to a dictionary."""
    return {column.name: getattr(model_instance, column.name) for column in model_instance.__table__.columns}


def decode_email(encoded_email: str) -> str:
    return base64.b64decode(encoded_email).decode("utf-8")


async def gather_user_ratings_by_product_type(user_email: str, db: Session) -> Dict[str, List[Any]]:
    user_ratings = {}
    for product_type, models in product_type_to_ranking_model.items():
        user_ratings[product_type] = []
        for model in models:
            ratings = (
                db.query(model, User.username)
                  .outerjoin(User, model.connoisseur == User.email)
                  .filter(
                      model.connoisseur.ilike(user_email),
                      not_(model.strain.ilike("%Test%")),
                      not_(model.cultivator.ilike("%Cultivar%")),
                      not_(model.cultivator.ilike("%Connoisseur%")),
                  )
                  .all()
            )
            ratings_list = []
            for ranking_record, username in ratings:
                record_dict = model_to_dict(ranking_record)
                record_dict["username"] = username or "Cult Member"
                record_dict["connoisseur"] = "cultmember@cannabiscult.co"
                ratings_list.append(record_dict)
            user_ratings[product_type].extend(ratings_list)
    for product_type, data in user_ratings.items():
        user_ratings[product_type] = convert_to_schema(product_type, data)
    return user_ratings


@router.get(
    "/get_my_ratings", response_model=Dict[str, List[Any]], dependencies=[Depends(settings.jwt_auth_dependency)]
)
async def get_my_ratings(user_email: str, db: Session = Depends(get_db)):
    if not user_email:
        raise HTTPException(status_code=400, detail="User email is required")
    try:
        decoded_email = decode_email(user_email)
        ratings = await gather_user_ratings_by_product_type(decoded_email, db)
        return ratings
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/check-existence/{product_type}")
async def check_existence(product_type: str, entry: StrainCultivator, db: Session = Depends(get_db)):
    models = product_type_to_model.get(product_type)
    if not models:
        raise HTTPException(status_code=404, detail="Product type not found")
    for model in models:
        exists = (
            db.query(model).filter(model.strain.ilike(entry.strain), model.cultivator.ilike(entry.cultivator)).first()
            is not None
        )
        if exists:
            return {"exists": True}
    return {"exists": False}


@router.get("/all/{search_term}", response_model=List[SearchResultItem])
async def get_search_matches(search_term: str, with_images_flag: bool = False, db: Session = Depends(get_db)):
    if not search_term or len(search_term) < 3:
        return []
    results = await search_strain(db, search_term, with_images_flag)
    if not results:
        raise HTTPException(status_code=404, detail="No matches found")
    return results


@router.get("/product-types", response_model=List[Any])
async def get_product_types(db: Session = Depends(get_db)):
    try:
        product_types = await get_all_product_types(db)
        if not product_types:
            raise HTTPException(status_code=404, detail="No product types found")
        return product_types
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/product-types/moluv/", response_model=List[Any])
async def get_product_types_for_moluv(db: Session = Depends(get_db)):
    try:
        product_types = await get_all_product_types(db)
        if not product_types:
            raise HTTPException(status_code=404, detail="No product types found")
        return [p for p in product_types if p in ["flower", "concentrate"]]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cultivators/{product_type}", response_model=List[Any], include_in_schema=False)
async def get_cultivators(
    product_type: str,
    product_type_dict=product_type_to_model,
    db: Session = Depends(get_db),
):
    if product_type == "Pre-roll":
        product_type = "Pre-Roll"
    models = product_type_dict.get(product_type)
    if not models:
        raise HTTPException(status_code=404, detail="Product type not found")

    all_cultivators = []
    for model in models:
        cultivators = get_cultivators_by_product_type(db, model)
        if cultivators:
            all_cultivators.extend(cultivators)

    if not all_cultivators:
        raise HTTPException(status_code=500, detail="An error occurred")

    return list(set(all_cultivators))


@router.get(
    "/strains/{product_type}/{cultivator}",
    response_model=List[str],
    include_in_schema=False,
)
async def get_strains(
    product_type: str,
    cultivator: str,
    product_type_dict=product_type_to_model,
    db: Session = Depends(get_db),
):
    if product_type == "Pre-roll":
        product_type = "Pre-Roll"
    models = product_type_dict.get(product_type)
    if not models:
        raise HTTPException(status_code=404, detail="Product type not found")
    all_strains = []
    for model in models:
        strains = get_strains_by_cultivator(db, model, cultivator)
        if strains:
            all_strains.extend(strains)
    if not all_strains:
        raise HTTPException(status_code=500, detail="An error occurred")
    return all_strains


@router.get(
    "/strains/{product_type}/moluv/",
    response_model=List[str],
    include_in_schema=False,
)
async def get_strains_for_molov_collab_route(
    product_type: str,
    db: Session = Depends(get_db),
):
    global product_type_to_model
    models = product_type_to_model.get(product_type)
    if not models:
        raise HTTPException(status_code=404, detail="Product type not found")
    all_strains = []
    for model in models:
        strains = get_strains_for_moluv_collab(db, model)
        if strains:
            all_strains.extend(strains)
    if not all_strains:
        raise HTTPException(status_code=500, detail="An error occurred")
    return [s for s in set(all_strains)]


@router.get(
    "/random/cultivator/{product_type}",
    response_model=Optional[str],
    include_in_schema=False,
)
async def get_random_cultivator_search(
    product_type: str,
    product_type_dict=product_type_to_model,
    db: Session = Depends(get_db),
):
    if product_type == "Pre-roll":
        product_type = "Pre-Roll"
    models = product_type_dict.get(product_type)
    if not models:
        raise HTTPException(status_code=404, detail="Product type not found")

    random_number = random.randint(0, 3)

    random_cultivator = get_random_cultivator(db, models[random_number])
    if not random_cultivator:
        raise HTTPException(status_code=404, detail="No cultivators found")

    return random_cultivator


async def run_aggregation_task(task_id, db, model_dict):
    try:
        result = await aggregate_ratings_by_strain(db, model_dict)
        tasks[task_id] = {"status": "completed", "data": result}
    except Exception as e:
        tasks[task_id] = {"status": "failed", "error": str(e)}


@router.get("/get_aggregated_strain_ratings")
async def get_aggregated_strain_ratings(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    task_id = str(uuid4())
    tasks[task_id] = {"status": "running"}
    background_tasks.add_task(run_aggregation_task, task_id, db, product_type_to_ranking_model)
    return {"message": "Task started", "task_id": task_id}


@router.get("/get_task_result/{task_id}")
async def get_task_result(
    task_id: str,
    model_dict: dict = product_type_to_ranking_model,
    db: Session = Depends(get_db),
):
    task = tasks.get(task_id)
    if not task:
        try:
            task_id = str(uuid4())
            await run_aggregation_task(task_id, db, model_dict)
        except Exception as e:
            raise HTTPException(status_code=404, detail=f"Task not found: {e}")
        else:
            task = tasks.get(task_id)
    return task


@router.get("/get-all-image-urls/", response_model=List[Any])
async def get_all_image_urls_route(limit=10, db: Session = Depends(get_db)):
    try:
        # Fetch data using the synchronous function
        product_data = get_all_card_paths(db, limit)
        # Asynchronously generate and stream URLs
        return StreamingResponse(generate_signed_urls(product_data), media_type="application/json")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/get-all-events/", response_model=List[CalendarEventQuery])
async def get_all_events_route(db: Session = Depends(get_db)):
    try:
        events = await get_all_events(db)
        return events
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/add-calendar-event/", status_code=201, dependencies=[Depends(settings.jwt_auth_dependency)])
async def add_calendar_event(event_data: CalendarEventQuery, db: Session = Depends(get_db)):
    try:
        success = await add_new_calendar_event(db, event_data.dict())
        if not success:
            raise HTTPException(
                status_code=409,
                detail="An error occurred during calendar event update or creation.",
            )
        return {"message": "Event added successfully"}
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/strains/{product_type}", response_model=List)
async def get_list_of_strains_for_terp_profile(product_type: str, db: Session = Depends(get_db)):
    try:
        strains_list = get_all_strains_by_product_type(db, product_type)
        if strains_list is None:
            raise HTTPException(status_code=404, detail="Strains not found")
        return strains_list
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/terps/{product_type}/{product_id}",
    response_model=Union[
        ProductWithTerpProfileSchema,
        FlowerTerpTableSchema,
        ConcentrateTerpTableSchema,
        EdibleTerpTableSchema,
        PreRollTerpTableSchema,
    ],
)
async def get_product_terp_profile(product_type: str, product_id: int, db: Session = Depends(get_db)):
    try:
        profile = await get_terp_profile_by_type(db, product_type, product_id)
        if profile is None:
            raise HTTPException(status_code=404, detail="Product not found")
        print(profile)
        return profile
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/strain-family-tree", response_model=Dict)
def get_family_tree(db: Session = Depends(get_db)):
    try:
        graph = build_strains_family_tree_graph(db)
        serialized_graph = serialize_graph(graph)
        return serialized_graph
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/terps/description", response_model=Union[ProductWithTerpProfileSchema, Dict[str, str]])
async def get_product_with_terp_profile_route(
    product_id: int = Query(None),
    product_type: str = Query(None),
    description_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
):
    terp_dict = await get_product_with_terp_profile(db, product_id, product_type, description_id)
    return terp_dict or {"message": "No Terp Profile Found"}


@router.get("/my_rankings")
async def get_user_ranking_for_product_route(
    product_type: str = Query(None),
    user_email: str = Query(None, alias="connoisseur"),
    product_id: Optional[int] = Query(None),
    strain: Optional[str] = Query(None),
    cultivator: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    user_ranking = await get_user_ranking_for_product(db, product_type, user_email, product_id, strain, cultivator)
    return user_ranking
