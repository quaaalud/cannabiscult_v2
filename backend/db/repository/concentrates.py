# -*- coding: utf-8 -*-

import traceback
from pathlib import Path
from sqlalchemy import func, and_
from sqlalchemy.orm import Session
from typing import Optional, Any, Dict, List
from db._supabase.connect_to_storage import return_image_url_from_supa_storage
from core.config import settings
from schemas.concentrates import (
    CreateConcentrateRanking,
)
from db.base import (
    Concentrate,
    Concentrate_Description,
    User,
    Vibe_Concentrate_Ranking,
    Concentrate_Ranking,
    TerpProfile,
)


def get_concentrate_data_and_path(db: Session, strain: str) -> Optional[Dict[str, Any]]:
    concentrate = db.query(Concentrate).filter((Concentrate.strain == strain)).first()
    if concentrate:
        return {
            "id": concentrate.concentrate_id,
            "cultivator": concentrate.cultivator,
            "strain": concentrate.strain,
            "url_path": return_image_url_from_supa_storage(str(Path(concentrate.card_path))),
            "voting_open": concentrate.voting_open,
            "is_mystery": concentrate.is_mystery,
        }
    return None


async def get_concentrate_by_strain_and_cultivator(
    db: Session, strain: str, cultivator: str
) -> Optional[Dict[str, Any]]:
    concentrate = (
        db.query(Concentrate).filter((Concentrate.strain == strain), (Concentrate.cultivator == cultivator)).first()
    )
    if concentrate:
        return {
            "id": concentrate.concentrate_id,
            "cultivator": concentrate.cultivator,
            "strain": concentrate.strain,
            "url_path": return_image_url_from_supa_storage(str(Path(concentrate.card_path))),
            "voting_open": concentrate.voting_open,
            "is_mystery": concentrate.is_mystery,
        }
    return None


def get_vibe_concentrate_strains(db: Session) -> Optional[List[str]]:
    concentrate_list = db.query(Concentrate).filter((Concentrate.cultivator == "Vibe")).all()
    if concentrate_list:
        return [concentrate.strain for concentrate in concentrate_list]
    return None


async def get_concentrate_and_description(
    db: Session,
    strain: str,
    cultivator: str = "",
    cultivar_email: str = "aaron.childs@thesocialoutfitus.com",
) -> Optional[Dict[Any, Any]]:
    try:
        query = (
            db.query(Concentrate, Concentrate_Description)
            .join(
                Concentrate_Description,
                Concentrate.concentrate_id == Concentrate_Description.concentrate_id,
            )
            .filter(Concentrate_Description.cultivar_email == cultivar_email)
        )
        if cultivator:
            query = query.filter(Concentrate.cultivator == cultivator)
        query = query.filter(Concentrate.strain == strain)
        concentrate_data = query.first()
        if not concentrate_data:
            query = db.query(Concentrate, Concentrate_Description).join(
                Concentrate_Description,
                Concentrate.concentrate_id == Concentrate_Description.concentrate_id,
            )
            if cultivator:
                query = query.filter(Concentrate.cultivator == cultivator)
            query = query.filter(Concentrate.strain == strain)
            concentrate_data = query.first()
        if concentrate_data:
            concentrate, description = concentrate_data
            concentrate_info = {
                "concentrate_id": concentrate.concentrate_id,
                "cultivator": concentrate.cultivator,
                "strain": concentrate.strain,
                "url_path": return_image_url_from_supa_storage(str(Path(concentrate.card_path))),
                "voting_open": concentrate.voting_open,
                "is_mystery": concentrate.is_mystery,
                "description_id": description.description_id,
                "description_text": description.description,
                "effects": description.effects,
                "lineage": description.lineage,
                "terpenes_list": description.terpenes_list,
                "cultivar": description.cultivar_email,
            }
            return concentrate_info
        return None
    except Exception as e:
        traceback.print_exc()
        print(f"Error fetching concentrate data and description: {e}")
        return None


async def get_concentrate_and_description_by_id(
    db: Session,
    concentrate_id: int,
    cultivar_email: str = "aaron.childs@thesocialoutfitus.com",
) -> Optional[Dict[Any, Any]]:
    try:
        query = (
            db.query(Concentrate, Concentrate_Description)
            .join(
                Concentrate_Description,
                Concentrate.concentrate_id == Concentrate_Description.concentrate_id,
                Concentrate.concentrate_id == concentrate_id,
            )
            .filter(Concentrate_Description.cultivar_email == cultivar_email)
        )
        concentrate_data = query.first()
        if not concentrate_data:
            query = db.query(Concentrate, Concentrate_Description).join(
                Concentrate_Description,
                Concentrate.concentrate_id == Concentrate_Description.concentrate_id,
                Concentrate.concentrate_id == concentrate_id,
                Concentrate_Description.concentrate_id == concentrate_id,
            )
            concentrate_data = query.first()
        if concentrate_data:
            concentrate, description = concentrate_data
            concentrate_info = {
                "concentrate_id": concentrate.concentrate_id,
                "cultivator": concentrate.cultivator,
                "strain": concentrate.strain,
                "url_path": return_image_url_from_supa_storage(str(Path(concentrate.card_path))),
                "voting_open": concentrate.voting_open,
                "is_mystery": concentrate.is_mystery,
                "description_id": description.description_id,
                "description_text": description.description,
                "effects": description.effects,
                "lineage": description.lineage,
                "terpenes_list": description.terpenes_list,
                "cultivar": description.cultivar_email,
            }
            return concentrate_info
        return None
    except Exception as e:
        traceback.print_exc()
        print(f"Error fetching concentrate data and description: {e}")
        return None


async def get_concentrate_rankings_by_id(db: Session, concentrate_id: int):
    avg_ratings = (
        db.query(
            func.avg(Concentrate_Ranking.color_rating),
            func.avg(Concentrate_Ranking.consistency_rating),
            func.avg(Concentrate_Ranking.smell_rating),
            func.avg(Concentrate_Ranking.flavor_rating),
            func.avg(Concentrate_Ranking.effects_rating),
            func.avg(Concentrate_Ranking.harshness_rating),
            func.avg(Concentrate_Ranking.residuals_rating),
        )
        .filter(Concentrate_Ranking.concentrate_id == concentrate_id)
        .first()
    )
    if not avg_ratings or any(rating is None for rating in avg_ratings):
        return {"strain": "no match found", "message": "Concentrate not found or incomplete data"}
    ratings_dict = {
        "concentrate_ranking_id": concentrate_id,
        "color_rating": round(avg_ratings[0], 2) if avg_ratings[0] is not None else None,
        "consistency_rating": (round(avg_ratings[1], 2) if avg_ratings[1] is not None else None),
        "smell_rating": round(avg_ratings[2], 2) if avg_ratings[2] is not None else None,
        "flavor_rating": round(avg_ratings[3], 2) if avg_ratings[3] is not None else None,
        "effects_rating": (round(avg_ratings[4], 2) if avg_ratings[4] is not None else None),
        "harshness_rating": (round(avg_ratings[5], 2) if avg_ratings[5] is not None else None),
        "residuals_rating": (round(avg_ratings[6], 2) if avg_ratings[6] is not None else None),
    }
    ratings_values = list(filter(None, avg_ratings))
    if ratings_values:
        overall_score = sum(ratings_values) / len(ratings_values)
        ratings_dict["overall_score"] = round(overall_score, 2)
    else:
        ratings_dict["overall_score"] = None
    return ratings_dict


@settings.retry_db
async def create_concentrate_ranking(ranking: CreateConcentrateRanking, db: Session):
    ranking_data_dict = ranking.dict()
    created_ranking = Concentrate_Ranking(**ranking_data_dict)
    try:
        db.add(created_ranking)
    except Exception:
        db.rollback()
    else:
        db.commit()
        db.refresh(created_ranking)
    return created_ranking


@settings.retry_db
async def update_or_create_concentrate_ranking(ranking: CreateConcentrateRanking, db: Session):
    existing_ranking = (
        db.query(Concentrate_Ranking)
        .filter(
            Concentrate_Ranking.cultivator == ranking.cultivator,
            Concentrate_Ranking.strain == ranking.strain,
            Concentrate_Ranking.connoisseur == ranking.connoisseur,
        )
        .first()
    )
    if existing_ranking:
        for key, value in ranking.dict().items():
            if value is not None:
                setattr(existing_ranking, key, value)
        try:
            db.commit()
            db.refresh(existing_ranking)
            return {"ranking_submitted": True}
        except Exception:
            db.rollback()
            raise
    else:
        await create_concentrate_ranking(ranking, db)
    return {"pre_roll_ranking": True}


@settings.retry_db
def create_vibe_concentrate_ranking(ranking: CreateConcentrateRanking, db: Session):
    ranking_data_dict = ranking.dict()
    created_ranking = Vibe_Concentrate_Ranking(**ranking_data_dict)
    try:
        db.add(created_ranking)
    except Exception:
        db.rollback()
    else:
        db.commit()
        db.refresh(created_ranking)
    finally:
        return created_ranking


async def return_average_concentrate_ratings(db: Session) -> List:
    return (
        db.query(
            Concentrate_Ranking.strain,
            Concentrate_Ranking.cultivator,
            Concentrate_Description.concentrate_id,
            Concentrate_Description.description_id,
            Concentrate_Description.description.label("description_text"),
            Concentrate_Description.effects,
            Concentrate_Description.lineage,
            Concentrate_Description.terpenes_list,
            Concentrate_Description.strain_category,
            Concentrate_Description.cultivar_email.label("cultivar"),
            User.username,
            Concentrate.voting_open,
            Concentrate.is_mystery,
            Concentrate.product_type,
            Concentrate.card_path,
            func.avg(Concentrate_Ranking.color_rating).label("color_rating"),
            func.avg(Concentrate_Ranking.consistency_rating).label("consistency_rating"),
            func.avg(Concentrate_Ranking.smell_rating).label("smell_rating"),
            func.avg(Concentrate_Ranking.flavor_rating).label("flavor_rating"),
            func.avg(Concentrate_Ranking.harshness_rating).label("harshness_rating"),
            func.avg(Concentrate_Ranking.residuals_rating).label("residuals_rating"),
            func.avg(Concentrate_Ranking.effects_rating).label("effects_rating"),
        )
        .join(Concentrate_Description, Concentrate_Ranking.concentrate_id == Concentrate_Description.concentrate_id)
        .join(User, User.email == Concentrate_Description.cultivar_email)
        .join(Concentrate, Concentrate.concentrate_id == Concentrate_Description.concentrate_id)
        .filter(
            Concentrate_Ranking.cultivator != "Connoisseur",
            ~Concentrate_Ranking.strain.ilike("%Test%"),
        )
        .group_by(
            Concentrate_Ranking.strain,
            Concentrate_Ranking.cultivator,
            Concentrate_Description.concentrate_id,
            Concentrate_Description.description_id,
            Concentrate_Description.description,
            Concentrate_Description.effects,
            Concentrate_Description.lineage,
            Concentrate_Description.terpenes_list,
            Concentrate_Description.strain_category,
            Concentrate_Description.cultivar_email,
            User.username,
            Concentrate.voting_open,
            Concentrate.is_mystery,
            Concentrate.product_type,
            Concentrate.card_path,
        )
        .all()
    )


async def return_all_available_descriptions_from_strain_id(db: Session, concentrate_id: int) -> List[Dict[str, Any]]:
    try:
        query = (
            db.query(
                Concentrate_Description,
                User.username,
                TerpProfile
            )
            .outerjoin(User, Concentrate_Description.cultivar_email == User.email)
            .outerjoin(
                TerpProfile,
                and_(
                    TerpProfile.description_id == Concentrate_Description.description_id,
                    TerpProfile.product_id == Concentrate_Description.concentrate_id,
                    TerpProfile.product_type == "concentrate",
                )
            )
            .filter(Concentrate_Description.concentrate_id == concentrate_id)
            .all()
        )
        if not query:
            return []
        descriptions = []
        for description, username, terp_profile in query:
            terpenes_map = {}
            if terp_profile:
                for col in TerpProfile.__table__.columns:
                    if col.name in ("description_id", "product_type", "product_id"):
                        continue
                    value = getattr(terp_profile, col.name, 0.0)
                    if value is not None and value != 0.0:
                        terpenes_map[col.name] = value
            descriptions.append({
                "concentrate_id": concentrate_id,
                "description_id": description.description_id,
                "description_text": description.description,
                "effects": description.effects,
                "lineage": description.lineage,
                "terpenes_list": description.terpenes_list,
                "username": username or "Cultivar",
                "strain_category": description.strain_category if description.strain_category else "cult_pack",
                "terpenes_map": terpenes_map
            })
        return descriptions
    except Exception as e:
        traceback.print_exc()
        print(f"Error fetching all descriptions for concentrate_id {concentrate_id}: {e}")
        return []
