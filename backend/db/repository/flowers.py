# -*- coding: utf-8 -*-

import base64
import traceback
from pathlib import Path
from sqlalchemy import func, not_
from sqlalchemy.orm import Session
from typing import Optional, Any, Dict, List, Union
from db.base import (
    Flower,
    Flower_Description,
    Flower_Ranking,
    User,
)
from schemas.flowers import (
    CreateFlowerRanking,
    FlowerReviewResponse,
)
from db._supabase.connect_to_storage import return_image_url_from_supa_storage, get_image_from_results
from core.config import settings


def convert_img_bytes_for_html(img_bytes):
    return base64.b64encode(img_bytes).decode()


def get_average_of_list(_list_of_floats: list[float]) -> float:
    return round(sum(_list_of_floats) / len(_list_of_floats) * 2) / 2


def get_flower_data_and_path(db: Session, strain: str, cultivator) -> Optional[Dict[str, Union[int, str, bool]]]:
    try:
        flower = db.query(Flower).filter((Flower.strain == strain, Flower.cultivator == cultivator)).first()
        return {
            "id": flower.flower_id,
            "cultivator": flower.cultivator,
            "strain": flower.strain,
            "url_path": return_image_url_from_supa_storage(str(Path(flower.card_path))),
            "voting_open": flower.voting_open,
            "is_mystery": flower.is_mystery,
            "product_type": flower.product_type,
        }
    except Exception as e:
        traceback.print_exc()
        print(f"Error fetching flower description: {e}")
        return None


def get_description_by_flower_id(
    flower_id: int, db: Session, cultivar_email: str = "aaron.childs@thesocialoutfitus.com"
) -> Optional[List[Dict[Any, Any]]]:
    try:
        flower_description = (
            db.query(Flower_Description)
            .filter(
                Flower_Description.flower_id == flower_id,
                Flower_Description.cultivar_email == cultivar_email,
            )
            .all()
        )
        img_path = str(Path(flower_description.card_path))
        results_bytes = return_image_url_from_supa_storage(img_path)
        flower_description["card_path"] = results_bytes
        return flower_description
    except Exception as e:
        traceback.print_exc()
        print(f"Error fetching flower description: {e}")
        return None


async def get_flower_and_description(
    db: Session,
    strain: str,
    cultivator: str = "",
    cultivar_email: str = "aaron.childs@thesocialoutfitus.com",
) -> Optional[Dict[str, Any]]:
    try:
        query = (
            db.query(Flower, Flower_Description)
            .join(Flower_Description, Flower.flower_id == Flower_Description.flower_id)
            .filter(Flower_Description.cultivar_email == cultivar_email)
        )
        if cultivator:
            query = query.filter(Flower.cultivator == cultivator)
        query = query.filter(Flower.strain == strain)
        flower_data = query.first()
        if not flower_data:
            query = db.query(Flower, Flower_Description).join(
                Flower_Description, Flower.flower_id == Flower_Description.flower_id
            )
            if cultivator:
                query = query.filter(Flower.cultivator == cultivator)
            query = query.filter(Flower.strain == strain)
            flower_data = query.first()
        if flower_data:
            flower, description = flower_data
            img_path = str(Path(flower.card_path))
            results_bytes = return_image_url_from_supa_storage(img_path)
            flower_info = {
                "flower_id": flower.flower_id,
                "cultivator": flower.cultivator,
                "strain": flower.strain,
                "url_path": results_bytes,
                "voting_open": flower.voting_open,
                "is_mystery": flower.is_mystery,
                "description_id": description.description_id,
                "description_text": description.description,
                "effects": description.effects,
                "lineage": description.lineage,
                "terpenes_list": description.terpenes_list,
                "cultivar": description.cultivar_email,
                "product_type": flower.product_type,
                "strain_category": description.strain_category if description.strain_category else "hybrid",
            }
            return flower_info
    except Exception as e:
        traceback.print_exc()
        raise e


def get_flower_and_description_by_id(
    db: Session,
    flower_id: Union[str, int],
    cultivar_email: str = "aaron.childs@thesocialoutfitus.com",
) -> Optional[Dict[str, Any]]:
    try:
        query = (
            db.query(Flower, Flower_Description)
            .join(Flower_Description, Flower.flower_id == Flower_Description.flower_id)
            .filter(
                int(Flower.flower_id) == int(flower_id),
                Flower_Description.cultivar_email == cultivar_email.lower().strip(),
            )
        )
        flower_data = query.first()
        if flower_data:
            flower, description = flower_data
            if not flower.is_mystery:
                cultivator = flower.cultivator
                description_text = description.description
                effects = description.effects
                lineage = description.lineage
                terpenes_list = description.terpenes_list
                strain = flower.strain
            else:
                strain = flower.strain
                cultivator = "Connoisseur"
                description_text = "Hidden"
                effects = "Hidden"
                lineage = "Hidden"
                terpenes_list = "Hidden"
            return {
                "flower_id": flower.flower_id,
                "cultivator": cultivator,
                "strain": strain,
                "url_path": return_image_url_from_supa_storage(str(Path(flower.card_path))),
                "voting_open": flower.voting_open,
                "is_mystery": flower.is_mystery,
                "description_id": description.description_id,
                "description_text": description_text,
                "effects": effects,
                "lineage": lineage,
                "terpenes_list": terpenes_list,
                "cultivar": description.cultivar_email,
                "product_type": flower.product_type,
                "strain_category": description.strain_category if description.strain_category else "hybrid",
            }
        return None
    except Exception as e:
        traceback.print_exc()
        print(f"Error fetching flower data and description: {e}")
        return None


def get_flower_strains(db: Session) -> Optional[List[str]]:
    try:
        flower_list = db.query(Flower).all()
        if flower_list:
            return [flower.strain for flower in flower_list]
    except Exception as e:
        traceback.print_exc()
        raise e


def get_hidden_flower_strains(db: Session) -> List[Optional[Dict[str, Union[int, str, bool]]]]:
    try:
        flower_list = db.query(Flower).filter((Flower.is_mystery == True)).all()
        if flower_list:
            return [get_flower_data_and_path(db, flower.strain, "connoisseur") for flower in flower_list]
    except Exception as e:
        traceback.print_exc()
        raise e


def get_review_data_and_path(db: Session, cultivator_select: str, strain_select: str) -> FlowerReviewResponse:
    review = (
        db.query(Flower_Ranking)
        .filter((Flower_Ranking.cultivator == cultivator_select) & (Flower_Ranking.strain == strain_select))
        .all()
    )
    if review:
        img_path = str(Path(review.card_path))
        results_bytes = get_image_from_results(img_path)
        struct_avg = get_average_of_list(review.structure)
        nose_avg = get_average_of_list(review.nose)
        flavor_avg = get_average_of_list(review.flavor)
        effects_avg = get_average_of_list(review.effects)
        total_avg = get_average_of_list([struct_avg, nose_avg, flavor_avg, effects_avg])
        return {
            "id": review.id,
            "strain": review.strain,
            "cultivator": review.cultivator,
            "overall": total_avg,
            "structure": struct_avg,
            "nose": nose_avg,
            "flavor": flavor_avg,
            "effects": effects_avg,
            "vote_count": review.vote_count,
            "card_path": results_bytes,
            "terpene_list": review.terpene_list,
            "url_path": return_image_url_from_supa_storage(img_path),
        }
    else:
        return {"strain": strain_select, "message": "Review not found"}


def return_selected_review(strain_selected: str, cultivator_selected: str, db: Session) -> FlowerReviewResponse:
    return get_review_data_and_path(
        db,
        cultivator_selected,
        strain_selected,
    )


@settings.retry_db
def create_flower_ranking(ranking_dict: CreateFlowerRanking, db: Session) -> CreateFlowerRanking:
    ranking_data_dict = ranking_dict.dict()
    created_ranking = Flower_Ranking(**ranking_data_dict)
    try:
        db.add(created_ranking)
    except Exception:
        db.rollback()
    else:
        db.commit()
        db.refresh(created_ranking)
    finally:
        return created_ranking


@settings.retry_db
def update_or_create_flower_ranking(ranking_dict: CreateFlowerRanking, db: Session) -> CreateFlowerRanking:
    existing_ranking = (
        db.query(Flower_Ranking)
        .filter(
            Flower_Ranking.cultivator == ranking_dict.cultivator,
            Flower_Ranking.strain == ranking_dict.strain,
            Flower_Ranking.connoisseur == ranking_dict.connoisseur,
        )
        .first()
    )
    if existing_ranking:
        for key, value in ranking_dict.dict().items():
            setattr(existing_ranking, key, value)
        try:
            db.commit()
            db.refresh(existing_ranking)
            return existing_ranking
        except Exception:
            db.rollback()
            raise
    else:
        return create_flower_ranking(ranking_dict, db)


async def return_average_flower_ratings(db: Session) -> List:
    return (
        db.query(
            Flower_Ranking.strain,
            Flower_Ranking.cultivator,
            Flower_Description.flower_id,
            Flower_Description.description_id,
            Flower_Description.description.label("description_text"),
            Flower_Description.effects,
            Flower_Description.lineage,
            Flower_Description.terpenes_list,
            Flower_Description.strain_category,
            Flower_Description.cultivar_email.label("cultivar"),
            User.username,
            Flower.voting_open,
            Flower.is_mystery,
            Flower.product_type,
            Flower.card_path,
            func.avg(Flower_Ranking.appearance_rating).label("appearance_rating"),
            func.avg(Flower_Ranking.smell_rating).label("smell_rating"),
            func.avg(Flower_Ranking.flavor_rating).label("flavor_rating"),
            func.avg(Flower_Ranking.effects_rating).label("effects_rating"),
            func.avg(Flower_Ranking.harshness_rating).label("harshness_rating"),
            func.avg(Flower_Ranking.freshness_rating).label("freshness_rating"),
        )
        .join(Flower_Description, Flower_Ranking.flower_id == Flower_Description.flower_id)
        .join(User, User.email == Flower_Description.cultivar_email)
        .join(Flower, Flower.flower_id == Flower_Description.flower_id)
        .filter(
            not_(Flower_Ranking.cultivator == "Connoisseur"),
            not_(Flower_Ranking.strain.ilike("%Test%")),
        )
        .group_by(
            Flower_Ranking.strain,
            Flower_Ranking.cultivator,
            Flower_Description.flower_id,
            Flower_Description.description_id,
            Flower_Description.description,
            Flower_Description.effects,
            Flower_Description.lineage,
            Flower_Description.terpenes_list,
            Flower_Description.strain_category,
            Flower_Description.cultivar_email,
            User.username,
            Flower.voting_open,
            Flower.is_mystery,
            Flower.product_type,
            Flower.card_path,
        )
        .all()
    )


async def return_all_available_descriptions_from_strain_id(db: Session, flower_id: int) -> List[Dict[str, Any]]:
    try:
        query = (
            db.query(
                Flower_Description,
                User.username
            )
            .join(User, Flower_Description.cultivar_email == User.email)
            .filter(Flower_Description.flower_id == flower_id)
            .all()
        )
        if not query:
            return []
        descriptions = []
        for description, username in query:
            descriptions.append({
                "flower_id": flower_id,
                "description_id": description.description_id,
                "description_text": description.description,
                "effects": description.effects,
                "lineage": description.lineage,
                "terpenes_list": description.terpenes_list,
                "username": username,
                "strain_category": description.strain_category if description.strain_category else "cult_pack",
            })
        return descriptions
    except Exception as e:
        traceback.print_exc()
        print(f"Error fetching all descriptions for flower_id {flower_id}: {e}")
        return []
