# -*- coding: utf-8 -*-

from pathlib import Path
from sqlalchemy.orm import Session
from typing import Optional, Any, Dict
from db.models.concentrates import Concentrate
from db._supabase.connect_to_storage import return_image_url_from_supa_storage


def get_concentrate_data_and_path(
        db: Session,
        strain_select: str) -> Optional[Dict[str, Any]]:
    concentrate = db.query(
        Concentrate
    ).filter(
        (Concentrate.strain == strain_select)
    ).first()
    if concentrate:
        return {
            'id': concentrate.concentrate_id,
            'cultivator': concentrate.cultivator,
            'strain': concentrate.strain,
            'url_path': return_image_url_from_supa_storage(
                str(Path(concentrate.card_path))
            ),
            'voting_open': concentrate.voting_open,
            'is_mystery': concentrate.is_mystery,
        }
    return None
