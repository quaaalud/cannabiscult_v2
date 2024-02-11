# -*- coding: utf-8 -*-

from pathlib import Path
from sqlalchemy.orm import Session
from typing import Optional, Any, Dict, List
from db.models.concentrates import Concentrate, Concentrate_Description
from db._supabase.connect_to_storage import return_image_url_from_supa_storage
import traceback


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
