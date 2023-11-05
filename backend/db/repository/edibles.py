# -*- coding: utf-8 -*-

from pathlib import Path
from sqlalchemy.orm import Session
from typing import Optional, Any, Dict
from db.models.edibles import MysteryEdible, VividEdible, VibeEdible
from db._supabase.connect_to_storage import return_image_url_from_supa_storage


def get_edible_data_and_path(
        db: Session,
        strain_select: str) -> Optional[Dict[str, Any]]:
    edible = db.query(
        MysteryEdible
    ).filter(
        (MysteryEdible.strain == strain_select)
    ).first()
    if edible:
        return {
            'mystery_id': edible.mystery_edible_id,
            'mystery_edible': edible.strain,
            'url_path': return_image_url_from_supa_storage(
                str(Path(edible.card_path))
            )
        }
    return None
  
  
def get_vivd_edible_data_by_strain(
        db: Session,
        edible_strain: int) -> Optional[Dict[str, Any]]:
    edible = db.query(
        VividEdible
    ).filter(
        (VividEdible.strain == edible_strain)
    ).first()
    if edible:
        return {
            'id': edible.vivid_edible_id,
            'edible': edible.strain,
            'url_path': return_image_url_from_supa_storage(
                str(Path(edible.card_path))
            )
        }
    return None
  
  
def get_vibe_edible_data_by_strain(
        db: Session,
        edible_strain: int) -> Optional[Dict[str, Any]]:
    edible = db.query(
        VibeEdible
    ).filter(
        (VibeEdible.strain == edible_strain)
    ).first()
    if edible:
        return {
            'id': edible.vibe_edible_id,
            'edible': edible.strain,
            'url_path': return_image_url_from_supa_storage(
                str(Path(edible.card_path))
            )
        }
    return None