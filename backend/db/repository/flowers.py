# -*- coding: utf-8 -*-

from pathlib import Path
from sqlalchemy.orm import Session
from typing import Optional, Any, Dict, List
from db.models.flowers import Flower
from db._supabase.connect_to_storage import return_image_url_from_supa_storage


def get_flower_data_and_path(
        db: Session,
        strain: str) -> Optional[Dict[str, Any]]:
    flower = db.query(
        Flower
    ).filter(
        (Flower.strain == strain)
    ).first()
    if flower:
        return {
            'id': flower.flower_id,
            'cultivator': flower.cultivator,
            'strain': flower.strain,
            'url_path': return_image_url_from_supa_storage(
                str(Path(flower.card_path))
            ),
            'voting_open': flower.voting_open,
            'is_mystery': flower.is_mystery,
        }
    return None


def get_vibe_flower_strains(db: Session) -> Optional[List[str]]:
    flower_list = db.query(
        Flower
    ).filter(
        (Flower.cultivator == 'Vibe')
    ).all()
    if flower_list:
        return [flower.strain for flower in flower_list]
    return None


def get_hidden_flower_strains(db: Session) -> Optional[List[str]]:
    flower_list = db.query(
        Flower
    ).filter(
        (Flower.is_mystery == True)
    ).all()
    if flower_list:
        return [get_flower_data_and_path(db, flower.strain) for flower in flower_list]
    return None
