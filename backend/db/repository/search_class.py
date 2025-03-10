#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 22 20:12:12 2023

@author: dale
"""

import random
import traceback
import networkx as nx
from datetime import datetime
from typing import Type, List, Dict, Any, Optional, Union
from sqlalchemy import inspect, func, or_, and_, not_, union_all
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session
from sqlalchemy.exc import ProgrammingError, SQLAlchemyError
from sqlalchemy.future import select
from core.config import settings
from schemas.search_class import (
    RatingModel,
    FlowerTerpTableSchema,
    ConcentrateTerpTableSchema,
    EdibleTerpTableSchema,
    PreRollTerpTableSchema,
    ProductResultSchema,
    DescriptionResultSchema,
    TerpProfileResultSchema,
    ProductWithTerpProfileSchema,
)
from schemas.product_types import AggregatedStrainRatingSchema, create_rating_schema
from db.base import (
    Base,
    Flower,
    Flower_Description,
    Flower_Ranking,
    Concentrate,
    Concentrate_Description,
    Concentrate_Ranking,
    Edible,
    VibeEdible,
    Edible_Description,
    Pre_Roll,
    Pre_Roll_Description,
    Pre_Roll_Ranking,
    TerpProfile,
    Product_Types,
    FlowerTerpTable,
    ConcentrateTerpTable,
    EdibleTerpTable,
    PreRollTerpTable,
    Current_Lineages,
    CalendarEvent,
    CalendarEventQuery,
    SimpleProductSchema,
    AggregatedStrainRating,
    User,
)
from schemas.flowers import GetFlowerRanking
from schemas.concentrates import GetConcentrateRanking
from schemas.pre_rolls import GetPreRollRanking
from db._supabase.connect_to_storage import return_image_url_from_supa_storage


PRODUCT_TABLE_MAPPINGS = {
    "flower": {"product": Flower, "description": Flower_Description, "schema": FlowerTerpTableSchema},
    "concentrate": {
        "product": Concentrate,
        "description": Concentrate_Description,
        "schema": ConcentrateTerpTableSchema,
    },
    "edible": {"product": Edible, "description": Edible_Description, "schema": EdibleTerpTableSchema},
    "pre_roll": {"product": Pre_Roll, "description": Pre_Roll_Description, "schema": PreRollTerpTableSchema},
    "vibeedible": {"product": VibeEdible, "description": Edible_Description, "schema": EdibleTerpTableSchema},
}

PRODUCT_TERP_TABLE_MAPPINGS = {
    "flower": FlowerTerpTable,
    "concentrate": ConcentrateTerpTable,
    "pre_roll": PreRollTerpTable,
    "edible": EdibleTerpTable,
}

RANKING_LOOKUP = {
    "flower": (
        Flower_Ranking,
        "flower_id",
        "connoisseur",
        GetFlowerRanking,
    ),
    "concentrate": (
        Concentrate_Ranking,
        "concentrate_id",
        "connoisseur",
        GetConcentrateRanking,
    ),
    "pre_roll": (
        Pre_Roll_Ranking,
        "pre_roll_id",
        "connoisseur",
        GetPreRollRanking,
    ),
}


async def get_user_ranking_for_product(
    db: Session,
    product_type: str,
    user_email: str,
    product_id: Optional[int] = None,
    strain: Optional[str] = None,
    cultivator: Optional[str] = None,
) -> Optional[
    Union[
        GetFlowerRanking,
        GetConcentrateRanking,
        GetPreRollRanking,
    ]
]:
    lookup = RANKING_LOOKUP.get(product_type.lower())
    if not lookup:
        return None
    RankingModel, id_field_name, email_field_name, RankingSchema = lookup
    query = (
        db.query(RankingModel, User.username)
        .outerjoin(User, getattr(RankingModel, email_field_name) == User.email)
        .filter(getattr(RankingModel, email_field_name).ilike(user_email))
    )
    if product_id is not None and hasattr(RankingModel, id_field_name):
        query = query.filter(getattr(RankingModel, id_field_name) == product_id)
    elif strain and cultivator:
        query = query.filter(
            RankingModel.strain.ilike(strain),
            RankingModel.cultivator.ilike(cultivator),
        )
    else:
        return None
    result = query.first()
    if not result:
        return None
    ranking_record, username = result
    schema_obj = RankingSchema.from_orm(ranking_record)
    schema_dict = schema_obj.dict()
    schema_dict["username"] = username or "Cult Member"
    schema_dict[email_field_name] = "cultmember@cannabiscult.co"
    return RankingSchema(**schema_dict)


async def get_terp_profile_by_type(db: Session, product_type: str, product_id: int) -> Union[
    FlowerTerpTableSchema,
    ConcentrateTerpTableSchema,
    EdibleTerpTableSchema,
    PreRollTerpTableSchema,
]:
    product_data = await get_product_with_terp_profile(db, product_id, product_type.lower().strip())
    if product_data is None:
        return None
    return product_data


async def get_data_by_strain(
    db: Session, model: Type[Base], strain: str, get_image_url_flag: bool = False
) -> List[Dict[str, Any]]:
    if model == VibeEdible:
        return []
    try:
        result = db.execute(
            select(model).filter(
                and_(
                    or_(
                        model.cultivator.ilike(f"%{strain}%"),
                        model.strain.ilike(f"%{strain}%"),
                    ),
                    and_(
                        not_(model.strain.ilike("%Test%")),
                        not_(model.cultivator.ilike("%Cultivar%")),
                        not_(model.cultivator.ilike("%Connoisseur%")),
                    ),
                )
            )
        )
        items = result.scalars().all()
        if get_image_url_flag:
            return [
                {
                    "cultivator": item.cultivator,
                    "strain": item.strain,
                    "type": model.__name__,
                    "url_path": return_image_url_from_supa_storage(str(item.card_path)),
                }
                for item in items
            ]
        else:
            return [
                {
                    "cultivator": item.cultivator,
                    "strain": item.strain,
                    "type": model.__name__,
                    "url_path": str(item.card_path),
                }
                for item in items
            ]
    except Exception as e:
        traceback.print_exc()
        print(f"Error fetching data for {model.__name__}: {e}")
        return []


async def search_strain(db: Session, strain: str, get_image_url_flag: bool = False) -> List[Dict[str, Any]]:
    flower_results = await get_data_by_strain(db, Flower, strain, get_image_url_flag)
    concentrate_results = await get_data_by_strain(db, Concentrate, strain, get_image_url_flag)
    try:
        general_edibles = await get_data_by_strain(db, Edible, strain, get_image_url_flag)
    except ProgrammingError:
        general_edibles = []
    vibe_edibles = await get_data_by_strain(db, VibeEdible, strain, get_image_url_flag)
    for item in vibe_edibles:
        item["type"] = "Edible"
    edible_results = [*general_edibles, *vibe_edibles]
    pre_roll_results = await get_data_by_strain(db, Pre_Roll, strain, get_image_url_flag)
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
            .where(model.cultivator != "Connoisseur")
            .filter(and_(model.cultivator != "Cultivar", not_(model.cultivator.ilike("%Connoisseur%"))))
            .distinct()
        )
        cultivators = result.scalars().all()
        return [cultivator for cultivator in cultivators]
    except Exception as e:
        traceback.print_exc()
        print(f"Error fetching cultivators for {model.__name__}: {e}")
        return []


def get_strains_by_cultivator(db: Session, model: Type[Base], cultivator: str) -> Optional[List[str]]:
    try:
        result = db.execute(
            select(model.strain)
            .where(model.cultivator == cultivator, model.cultivator.not_in(["Connoisseur", "Cultivar"]))
            .filter(
                not_(model.strain.ilike("%Test%")),
                not_(model.strain.ilike("%MOLUV%")),
                and_(
                    not_(model.strain.ilike("%Test%")),
                    not_(model.cultivator.ilike("%Cultivar%")),
                    not_(model.cultivator.ilike("%Connoisseur%")),
                ),
            )
        )
        strains = result.scalars().all()
        return [strain for strain in strains if "test" not in strain.lower()]
    except Exception as e:
        traceback.print_exc()
        print(f"Error fetching strains for {model.__name__} & cultivator {cultivator}: {e}")
        return None


def get_strains_for_moluv_collab(db: Session, model: Type[Base]) -> Optional[List[str]]:
    try:
        result = db.execute(
            select(model.strain).where(model.cultivator == "Connoisseur").filter(model.strain.ilike("%MOLUV%"))
        )
        strains = result.scalars().all()
        return strains
    except Exception as e:
        traceback.print_exc()
        print(f"Error fetching moluv strains for {model.__name__}: {e}")
        return None


def get_random_cultivator(db: Session, model: Type[Base]) -> str:
    try:
        result = db.execute(select(model.cultivator).distinct().order_by(func.random()).limit(1))
        random_cultivator = result.scalar_one()
        return random_cultivator
    except Exception as e:
        traceback.print_exc()
        print(f"Error fetching random cultivator for {model.__name__}: {e}")
        return ""


def get_random_strain(db: Session, model: Type[Base]) -> str:
    try:
        result = db.execute(select(model.strain).distinct().order_by(func.random()).limit(1))
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
            columns = [c.name for c in inspect(model).c]
            rating_columns = [col for col in columns if col.endswith("_rating")]
            selection = [model.strain, model.cultivator] + [
                func.avg(func.nullif(getattr(model, col), None)).label(col) for col in rating_columns
            ]
            query = (
                db.query(*selection)
                .filter(
                    not_(model.cultivator.ilike("%Cultivar")),
                    not_(model.cultivator.ilike("Connoisseur")),
                    not_(model.strain.ilike("%Test%")),
                    or_(*[getattr(model, col) is not None for col in rating_columns]),
                )
                .group_by(model.strain, model.cultivator)
            )
            ratings = query.all()
            for rating in ratings:
                rating_data = {
                    "product_type": product_type,
                    "strain": rating.strain,
                    "cultivator": rating.cultivator,
                }
                sum_ratings = 0
                count_ratings = 0
                for col in rating_columns:
                    rating_value = getattr(rating, col)
                    if rating_value is not None:
                        rounded_rating = round(float(rating_value), 2)
                        rating_data[col] = rounded_rating
                        sum_ratings += rounded_rating
                        count_ratings += 1
                if count_ratings > 0:
                    rating_data["cult_rating"] = round(sum_ratings / count_ratings, 2)
                else:
                    rating_data["cult_rating"] = None
                all_ratings.append(rating_data)
    return all_ratings


async def aggregate_strain_ratings_by_model(db: Session, model: Type, product_type: str):
    columns = [c.name for c in inspect(model).c]
    rating_columns = [col for col in columns if col.endswith("_rating")]
    selection = [
        model.strain,
        model.cultivator,
        *(func.avg(func.nullif(getattr(model, col), None)).label(col) for col in rating_columns),
    ]
    query = (
        db.query(*selection)
        .filter(
            not_(model.cultivator.ilike("%Cultivar")),
            not_(model.cultivator.ilike("Connoisseur")),
            not_(model.strain.ilike("%Test%")),
            or_(*(getattr(model, col).isnot(None) for col in rating_columns)),
        )
        .group_by(model.strain, model.cultivator)
    )
    results = query.all()
    Schema = create_rating_schema(model)
    aggregated_ratings = []
    for result in results:
        rating_dict = {
            "product_type": product_type,
            "strain": result.strain,
            "cultivator": result.cultivator,
        }
        sum_ratings = 0
        count_ratings = 0

        for col in rating_columns:
            rating_value = getattr(result, col)
            rounded_value = round(rating_value, 2) if rating_value is not None else None
            rating_dict[col] = rounded_value
            if rounded_value is not None:
                sum_ratings += rounded_value
                count_ratings += 1

        rating_dict["cult_rating"] = round(sum_ratings / count_ratings, 2) if count_ratings else None
        aggregated_ratings.append(Schema(**rating_dict))
    return aggregated_ratings


async def batch_aggregate_all_strains(db: Session, model_dict: Dict[str, List[Type]]) -> List[Dict]:
    all_aggregated_ratings = []
    for product_type, models in model_dict.items():
        for model in models:
            ratings = await aggregate_strain_ratings_by_model(db, model, product_type)
            all_aggregated_ratings.extend([rating.dict() for rating in ratings])
    return all_aggregated_ratings


def upsert_aggregated_strain_ratings(db: Session, ratings: List[AggregatedStrainRatingSchema]) -> None:
    stmt = insert(AggregatedStrainRating).values(
        [
            {
                "product_type": rating.product_type,
                "strain": rating.strain,
                "cultivator": rating.cultivator,
                "cult_rating": rating.cult_rating,
                "ratings": rating.ratings,
            }
            for rating in ratings
        ]
    )
    update_dict = {
        "cult_rating": stmt.excluded.cult_rating,
        "ratings": stmt.excluded.ratings,
    }
    stmt = stmt.on_conflict_do_update(
        index_elements=["product_type", "strain", "cultivator"],
        set_=update_dict,
    )
    db.execute(stmt)
    db.commit()


def get_all_card_paths(db: Session, limit=10) -> List[dict]:
    select_flower = select(Flower.cultivator, Flower.strain, Flower.card_path, Flower.product_type).filter(
        Flower.strain.notilike("%Test%"), Flower.cultivator != "Connoisseur"
    )
    select_concentrate = select(
        Concentrate.cultivator,
        Concentrate.strain,
        Concentrate.card_path,
        Concentrate.product_type,
    ).filter(Concentrate.strain.notilike("%Test%"), Concentrate.cultivator != "Connoisseur")
    select_pre_roll = select(Pre_Roll.cultivator, Pre_Roll.strain, Pre_Roll.card_path, Pre_Roll.product_type).filter(
        Pre_Roll.strain.notilike("%Test%"), Pre_Roll.cultivator != "Connoisseur"
    )
    select_edible = select(Edible.cultivator, Edible.strain, Edible.card_path, Edible.product_type).filter(
        Edible.strain.notilike("%Test%"), Edible.cultivator != "Connoisseur"
    )
    combined_query = union_all(select_flower, select_concentrate, select_pre_roll, select_edible)
    subquery = combined_query.alias("subquery")
    total_rows = db.execute(select(func.count()).select_from(subquery)).scalar()
    if total_rows == 0:
        return []
    random_offset = random.randint(0, total_rows - 1)
    result = db.execute(combined_query.offset(random_offset).limit(limit)).fetchall()
    additional_needed = int(limit) - len(result)
    if additional_needed > 0:
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
    yield "[".encode("utf-8")
    first = True
    for product in product_data:
        try:
            signed_url = return_image_url_from_supa_storage(str(product["card_path"]))
            product_info = SimpleProductSchema(
                cultivator=product["cultivator"],
                strain=product["strain"],
                signed_url=signed_url,
                product_type=product["product_type"],
            ).json()
            if not first:
                yield ", ".encode("utf-8")
            yield product_info.encode("utf-8")
            first = False
        except Exception as e:
            print(f"Failed to generate URL for {product['card_path']}: {e}")
    yield "]".encode("utf-8")


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
        existing_event = (
            db.execute(
                select(CalendarEvent).filter_by(summary=event_data["summary"], start_date=event_data["start_date"])
            )
            .scalars()
            .first()
        )
        if existing_event:
            return await update_calendar_event(db, event_data["summary"], event_data["start_date"], event_data)
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


async def update_calendar_event(db: Session, summary: str, start_date: str, new_data: dict) -> bool:
    try:
        event = db.execute(select(CalendarEvent).filter_by(summary=summary, start_date=start_date)).scalars().first()
        if not event:
            print("No matching event found for update.")
            return False
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


async def get_card_path_by_details(db: Session, product_type: str, strain: str, cultivator: str) -> Optional[str]:
    product_type = product_type.lower().replace("-", "_")
    model_mapping = PRODUCT_TABLE_MAPPINGS.get(product_type)
    if not model_mapping:
        return None
    model = model_mapping.get("product", None)
    if not model:
        return None
    try:
        result = db.execute(
            select(model.card_path)
            .where(
                model.strain == strain,
                model.cultivator == cultivator,
                not_(model.strain.ilike("%Test%")),
            )
            .limit(1)
        ).scalar_one()
        return result
    except Exception as e:
        print(f"Error for card_path on {model.__name__}, {strain}, {cultivator}: {e}")
        return None


def get_all_strains_by_product_type(db: Session, product_type: str) -> List[Dict[str, any]]:
    product_type = product_type.replace("-", "_")
    model_mapping = PRODUCT_TABLE_MAPPINGS.get(product_type.lower())
    model = model_mapping.get("product", None)
    if not model_mapping or not model:
        raise ValueError("Invalid product type provided")
    try:
        primary_key = [key.name for key in inspect(model).primary_key][0]
        data = (
            db.query(getattr(model, primary_key), model.strain, model.cultivator)
            .where(
                model.strain.notilike("%Test%"),
                model.cultivator.notilike("%Connoisseur%"),
                model.cultivator.notilike("%Cultivar%"),
            )
            .order_by(model.strain)
            .all()
        )
        return [{"product_id": item[0], "strain": item[1], "cultivator": item[2]} for item in data]
    except Exception as e:
        print(f"Error fetching strains for {product_type}: {e}")
        return []


def build_strains_family_tree_graph(db: Session):
    strains = db.query(Current_Lineages).all()
    G = nx.DiGraph()
    for strain in strains:
        current_strain = strain.strain.strip()
        if current_strain not in G:
            G.add_node(current_strain)
        if strain.lineage:
            parents = strain.lineage.split(" X ")
            for parent in parents:
                parent = parent.strip()
                if parent not in G:
                    G.add_node(parent)
                G.add_edge(parent, current_strain)
    return G


def serialize_graph(graph):
    nodes = [{"id": node} for node in graph.nodes()]
    edges = [{"source": edge[0], "target": edge[1]} for edge in graph.edges()]
    return {"nodes": nodes, "edges": edges}


async def get_product_with_terp_profile(db: Session, product_id: int, product_type: str, description_id: int = None):
    product_type = product_type.lower().replace("-", "_")
    if product_type not in PRODUCT_TABLE_MAPPINGS:
        raise ValueError(f"Invalid product type: {product_type}")
    product_mapping = PRODUCT_TABLE_MAPPINGS[product_type]
    product_table = product_mapping["product"]
    description_table = product_mapping["description"]
    query = (
        db.query(product_table, description_table, User.username)
        .outerjoin(
            description_table,
            product_table.__table__.c[product_table.__table__.primary_key.columns.keys()[0]]
            == description_table.__table__.c[product_table.__table__.primary_key.columns[0].name],
        )
        .outerjoin(User, description_table.cultivar_email == User.email)
        .filter(product_table.__table__.c[product_table.__table__.primary_key.columns.keys()[0]] == product_id)
    )
    if description_id:
        query = query.filter(description_table.description_id == description_id)
    product_data = query.first()
    if not product_data:
        return None
    product, description, username = product_data
    if not description_id:
        description_id = description.description_id
    terp_profile = (
        db.query(TerpProfile)
        .filter_by(product_type=product_type, product_id=product_id, description_id=description_id)
        .first()
    )
    product_dict = {col.name: getattr(product, col.name) for col in product.__table__.columns}
    description_dict = (
        {col.name: getattr(description, col.name) for col in description.__table__.columns} if description else {}
    )
    description_dict["username"] = username
    terp_profile_dict = (
        {col.name: getattr(terp_profile, col.name) for col in TerpProfile.__table__.columns} if terp_profile else {}
    )
    terp_profile_dict = {k: v for k, v in terp_profile_dict.items() if isinstance(v, (int, float)) and v != 0}
    product_dict["product_id"] = product_id
    description_dict["product_id"] = product_id
    product_result = ProductResultSchema(**product_dict)
    description_result = DescriptionResultSchema(**description_dict)
    terp_result = TerpProfileResultSchema(
        description_id=description_id,
        product_id=product_id,
        terp_values=terp_profile_dict,
    )
    return ProductWithTerpProfileSchema(
        product=product_result,
        description=description_result,
        terp_profile=terp_result,
    )


async def upsert_terp_profile(
    db: Session,
    description_id: int,
    product_id: int,
    product_type: str,
    terpenes_map: Dict[str, float],
) -> TerpProfile:
    try:
        existing_profile = (
            db.query(TerpProfile)
            .filter_by(
                description_id=description_id,
                product_id=product_id,
                product_type=product_type,
            )
            .first()
        )
        if not existing_profile:
            new_profile = TerpProfile(
                description_id=description_id,
                product_id=product_id,
                product_type=product_type,
            )
            for terp_name, terp_value in terpenes_map.items():
                setattr(new_profile, terp_name, (terp_value / 100))
            db.add(new_profile)
            db.commit()
            db.refresh(new_profile)
            return new_profile
        for terp_name, terp_value in terpenes_map.items():
            setattr(existing_profile, terp_name, (terp_value / 100))
        db.commit()
        db.refresh(existing_profile)
        return existing_profile
    except Exception as e:
        db.rollback()
        raise e
