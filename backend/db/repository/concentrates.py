# -*- coding: utf-8 -*-

from pathlib import Path
from sqlalchemy.orm import Session
from typing import Optional, Any, Dict, List
from db.models.concentrates import Concentrate
from db._supabase.connect_to_storage import return_image_url_from_supa_storage


def get_concentrate_data_and_path(
        db: Session,
        strain: str) -> Optional[Dict[str, Any]]:
    concentrate = db.query(
        Concentrate
    ).filter(
        (Concentrate.strain == strain)
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


def get_vibe_concentrate_strains(db: Session) -> Optional[List[str]]:
    concentrate_list = db.query(
        Concentrate
    ).filter(
        (Concentrate.cultivator == 'Vibe')
    ).all()
    if concentrate_list:
        return [concentrate.strain for concentrate in concentrate_list]
    return None
