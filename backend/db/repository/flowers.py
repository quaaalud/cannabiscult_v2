# -*- coding: utf-8 -*-

from pathlib import Path
from sqlalchemy.orm import Session
from typing import Optional, Any, Dict, List
from db.models.flowers import Flower, Flower_Description
from db._supabase.connect_to_storage import return_image_url_from_supa_storage
import traceback


def get_flower_data_and_path(db: Session, strain: str) -> Optional[Dict[str, Any]]:
    try:
        flower = db.query(Flower).filter((Flower.strain == strain)).first()
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
            }
            return flower_info

        return None

    except Exception as e:
        traceback.print_exc()
        print(f"Error fetching flower data and description: {e}")
        return None


def get_flower_and_description_by_id(
    db: Session,
    flower_id: str,
    cultivar_email: str = "aaron.childs@thesocialoutfitus.com",
) -> Optional[Dict[str, Any]]:
    try:
        query = (
            db.query(Flower, Flower_Description)
            .join(Flower_Description, Flower.flower_id == Flower_Description.flower_id)
            .filter(
                Flower.flower_id == flower_id, Flower_Description.cultivar_email == cultivar_email
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

            flower_info = {
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
            }

            return flower_info
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
        print(f"Error fetching flower description: {e}")
        return None


def get_hidden_flower_strains(db: Session) -> Optional[List[str]]:
    try:
        flower_list = db.query(Flower).filter((Flower.is_mystery == True)).all()
        if flower_list:
            return [get_flower_data_and_path(db, flower.strain) for flower in flower_list]
    except Exception as e:
        traceback.print_exc()
        print(f"Error fetching flower description: {e}")
        return None
