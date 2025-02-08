# -*- coding: utf-8 -*-

import traceback
from pathlib import Path
from sqlalchemy.orm import Session
from typing import Optional, Any, Dict, List
from db.base import Concentrate, Concentrate_Description
from db._supabase.connect_to_storage import return_image_url_from_supa_storage
from core.config import settings
from schemas.concentrates import (
    CreateConcentrateRanking,
)
from db.base import (
    Vibe_Concentrate_Ranking,
    Concentrate_Ranking,
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
        db.query(Concentrate)
        .filter((Concentrate.strain == strain), (Concentrate.cultivator == cultivator))
        .first()
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
