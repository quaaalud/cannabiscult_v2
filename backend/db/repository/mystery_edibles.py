# -*- coding: utf-8 -*-

from pathlib import Path
from sqlalchemy.orm import Session
from db.models.mystery_edibles import MysteryEdible
from db._supabase.connect_to_storage import return_image_url_from_supa_storage


def get_edible_data_and_path(
        db: Session,
        strain_select: str) -> MysteryEdible:
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