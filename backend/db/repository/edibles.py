# -*- coding: utf-8 -*-

from pathlib import Path
from sqlalchemy.orm import Session
from typing import Optional, Any, Dict
from db.base import Edible, VibeEdible, Edible_Ranking, Vibe_Edible_Ranking
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
