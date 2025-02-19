# -*- coding: utf-8 -*-

import traceback
from pathlib import Path
from sqlalchemy import func, not_, or_, and_
from sqlalchemy.orm import Session
from typing import Optional, Any, Dict, List
from db.base import Edible, VibeEdible, Edible_Description, Edible_Ranking, Vibe_Edible_Ranking, User
from schemas.edibles import CreateEdibleRanking, CreateVibeEdibleRanking
from db._supabase.connect_to_storage import return_image_url_from_supa_storage
from core.config import settings


def get_edible_data_and_path(db: Session, strain_select: str) -> Optional[Dict[str, Any]]:
    edible = db.query(Edible).filter((Edible.strain == strain_select)).first()
    if edible:
        return {
            "id": edible.edible_id,
            "edible": edible.strain,
            "url_path": return_image_url_from_supa_storage(str(Path(edible.card_path))),
        }
    return None


def get_vibe_edible_data_by_strain(db: Session, edible_strain: int) -> Optional[Dict[str, Any]]:
    edible = db.query(VibeEdible).filter((VibeEdible.strain == edible_strain)).first()
    if edible:
        return {
            "id": edible.vibe_edible_id,
            "edible": edible.strain,
            "url_path": return_image_url_from_supa_storage(str(Path(edible.card_path))),
        }
    return None


async def get_edible_and_description(
    db: Session,
    strain: str,
    cultivator: str = "",
    cultivar_email: str = "aaron.childs@thesocialoutfitus.com",
) -> Optional[Dict[str, Any]]:
    try:
        query = (
            db.query(Edible, Edible_Description)
            .join(Edible_Description, Edible.edible_id == Edible_Description.edible_id)
            .filter(Edible_Description.cultivar_email == cultivar_email)
        )
        if cultivator:
            query = query.filter(Edible.cultivator == cultivator)
        query = query.filter(Edible.strain == strain)
        edible_data = query.first()
        if not edible_data:
            query = db.query(Edible, Edible_Description).join(
                Edible_Description, Edible.edible_id == Edible_Description.edible_id
            )
            if cultivator:
                query = query.filter(Edible.cultivator == cultivator)
            query = query.filter(Edible.strain == strain)
            edible_data = query.first()
        if edible_data:
            edible, description = edible_data
            img_path = str(Path(edible.card_path))
            results_bytes = return_image_url_from_supa_storage(img_path)
            edible_info = {
                "edible_id": edible.edible_id,
                "cultivator": edible.cultivator,
                "strain": edible.strain,
                "url_path": results_bytes,
                "voting_open": edible.voting_open,
                "is_mystery": edible.is_mystery,
                "description_id": description.description_id,
                "description_text": description.description,
                "effects": description.effects,
                "lineage": description.lineage,
                "terpenes_list": description.terpenes_list,
                "cultivar": description.cultivar_email,
                "product_type": edible.product_type,
                "strain_category": description.strain_category if description.strain_category else "cult_pack",
            }
            return edible_info
    except Exception as e:
        traceback.print_exc()
        raise e


@settings.retry_db
def create_edible_ranking(edible_ranking: CreateEdibleRanking, db: Session):
    ranking_data_dict = edible_ranking.dict()
    created_edible_ranking = Edible_Ranking(**ranking_data_dict)
    try:
        db.add(created_edible_ranking)
    except Exception:
        db.rollback()
    else:
        db.commit()
        db.refresh(created_edible_ranking)
    finally:
        return created_edible_ranking


@settings.retry_db
def update_or_create_edible_ranking(edible_ranking: CreateEdibleRanking, db: Session) -> CreateEdibleRanking:
    try:
        existing_ranking = (
            db.query(Edible_Ranking)
            .filter(
                or_(
                    Edible_Ranking.edible_id == edible_ranking.edible_id,
                    and_(
                        Edible_Ranking.cultivator.ilike(edible_ranking.cultivator),
                        Edible_Ranking.strain.ilike(edible_ranking.strain)
                    )
                ),
                Edible_Ranking.connoisseur.ilike(edible_ranking.connoisseur.lower()),
            )
            .first()
        )
        if not existing_ranking:
            return create_edible_ranking(edible_ranking, db)
        for key, value in edible_ranking.dict().items():
            setattr(existing_ranking, key, value)
            db.commit()
            db.refresh(existing_ranking)
        return existing_ranking
    except Exception:
        db.rollback()
        raise


@settings.retry_db
def create_vibe_edible_ranking(edible_ranking: CreateVibeEdibleRanking, db: Session):
    ranking_data_dict = edible_ranking.dict()
    created_edible_ranking = Vibe_Edible_Ranking(**ranking_data_dict)
    try:
        db.add(created_edible_ranking)
    except Exception:
        db.rollback()
    else:
        db.commit()
        db.refresh(created_edible_ranking)
    finally:
        return created_edible_ranking


async def return_average_edible_ratings(db: Session) -> List:
    return (
        db.query(
            Edible_Ranking.strain,
            Edible_Ranking.cultivator,
            Edible_Ranking.flower_id,
            Edible_Description.description_id,
            Edible_Description.description.label("description_text"),
            Edible_Description.effects,
            Edible_Description.lineage,
            Edible_Description.terpenes_list,
            Edible_Description.strain_category,
            Edible_Description.cultivar_email.label("cultivar"),
            User.username,
            Edible.voting_open,
            Edible.is_mystery,
            Edible.product_type,
            Edible.card_path,
            func.avg(Edible_Ranking.appearance_rating).label("appearance_rating"),
            func.avg(Edible_Ranking.aftertaste_rating).label("aftertaste_rating"),
            func.avg(Edible_Ranking.flavor_rating).label("flavor_rating"),
            func.avg(Edible_Ranking.effects_rating).label("effects_rating"),
        )
        .join(Edible_Description, Edible_Ranking.flower_id == Edible_Description.edible_id)
        .join(User, User.email == Edible_Description.cultivar_email)
        .join(Edible, Edible.edible_id == Edible_Description.edible_id)
        .filter(
            not_(Edible_Ranking.cultivator == "Connoisseur"),
            not_(Edible_Ranking.strain.ilike("%Test%")),
        )
        .group_by(
            Edible_Ranking.strain,
            Edible_Ranking.cultivator,
            Edible_Description.edible_id,
            Edible_Description.description_id,
            Edible_Description.description,
            Edible_Description.effects,
            Edible_Description.lineage,
            Edible_Description.terpenes_list,
            Edible_Description.strain_category,
            Edible_Description.cultivar_email,
            User.username,
            Edible.voting_open,
            Edible.is_mystery,
            Edible.product_type,
            Edible.card_path,
        )
        .all()
    )


async def return_all_available_descriptions_from_strain_id(db: Session, edible_id: int) -> List[Dict[str, Any]]:
    try:
        query = (
            db.query(
                Edible_Description,
                User.username
            )
            .outerjoin(User, Edible_Description.cultivar_email == User.email)
            .filter(Edible_Description.edible_id == edible_id)
            .all()
        )
        if not query:
            return []
        descriptions = []
        for description, username in query:
            descriptions.append({
                "edible_id": edible_id,
                "description_id": description.description_id,
                "description_text": description.description,
                "effects": description.effects,
                "lineage": description.lineage,
                "terpenes_list": description.terpenes_list,
                "username": username or "Cultivar",
                "strain_category": description.strain_category if description.strain_category else "cult_pack",
            })
        return descriptions
    except Exception as e:
        traceback.print_exc()
        print(f"Error fetching all descriptions for edible_id {edible_id}: {e}")
        return []
