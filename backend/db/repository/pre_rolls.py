#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan 21 13:53:38 2024

@author: dale
"""

from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy.future import select
from typing import Optional, List, Dict, Any
from db.models.pre_rolls import Pre_Roll, Pre_Roll_Description, Pre_Roll_Ranking
from schemas.pre_rolls import PreRollRankingSchema
from db._supabase.connect_to_storage import (
    return_image_url_from_supa_storage,
    get_image_from_results,
)
import traceback
from pathlib import Path
from core.config import settings


def get_average_of_list(_list_of_floats: list[float]) -> float:
    if isinstance(_list_of_floats, list):
        return round(((sum(_list_of_floats) / len(_list_of_floats) * 2) / 2), 2)
    else:
        return round((_list_of_floats * 2) / 2, 2)


def calculate_overall_score(
    *vals,
):
    values_list = [*vals]
    return get_average_of_list(values_list)



async def get_pre_roll_data_and_path(db: Session, strain: str) -> Optional[Dict[str, Any]]:
    try:
        result = db.execute(select(Pre_Roll).where(Pre_Roll.strain == strain))
        pre_roll = result.scalars().first()
        if pre_roll:
            return {
                "id": pre_roll.pre_roll_id,
                "cultivator": pre_roll.cultivator,
                "strain": pre_roll.strain,
                "url_path": return_image_url_from_supa_storage(str(Path(pre_roll.card_path))),
                "voting_open": pre_roll.voting_open,
                "is_mystery": pre_roll.is_mystery,
            }
    except Exception as e:
        traceback.print_exc()
        print(f"Error fetching pre roll data: {e}")
    return None


async def get_pre_roll_by_strain_and_cultivator(
    db: Session, strain: str, cultivator: str
) -> Optional[Dict[str, Any]]:
    try:
        result = db.execute(
            select(Pre_Roll).where(Pre_Roll.strain == strain, Pre_Roll.cultivator == cultivator)
        )
        pre_roll = result.scalars().first()
        if pre_roll:
            return {
                "id": pre_roll.pre_roll_id,
                "cultivator": pre_roll.cultivator,
                "strain": pre_roll.strain,
                "url_path": return_image_url_from_supa_storage(str(Path(pre_roll.card_path))),
                "voting_open": pre_roll.voting_open,
                "is_mystery": pre_roll.is_mystery,
            }
    except Exception as e:
        traceback.print_exc()
        print(f"Error fetching pre roll by strain and cultivator: {e}")
    return None


async def get_pre_roll_strains_by_cultivator(db: Session, cultivator: str) -> Optional[List[str]]:
    try:
        result = db.execute(select(Pre_Roll.strain).where(Pre_Roll.cultivator == cultivator))
        strains = result.scalars().all()
        return strains
    except Exception as e:
        traceback.print_exc()
        print(f"Error fetching pre roll strains by cultivator: {e}")
    return None


async def get_pre_roll_and_description(
    db: Session,
    strain: str,
    cultivar_email: str = "aaron.childs@thesocialoutfitus.com",
    cultivator: str = "",
) -> Optional[Dict[str, Any]]:
    try:
        query = (
            db.query(Pre_Roll, Pre_Roll_Description)
            .join(Pre_Roll_Description, Pre_Roll.pre_roll_id == Pre_Roll_Description.pre_roll_id)
            .filter(Pre_Roll_Description.cultivar_email == cultivar_email)
        )

        if cultivator:
            query = query.filter(Pre_Roll.cultivator == cultivator)

        query = query.filter(Pre_Roll.strain == strain)
        pre_roll_data = query.first()

        if not pre_roll_data:
            query = db.query(Pre_Roll, Pre_Roll_Description).join(
                Pre_Roll_Description, Pre_Roll.pre_roll_id == Pre_Roll_Description.pre_roll_id
            )

            if cultivator:
                query = query.filter(Pre_Roll.cultivator == cultivator)

            query = query.filter(Pre_Roll.strain == strain)
            pre_roll_data = query.first()

        if pre_roll_data:
            pre_roll, description = pre_roll_data
            return {
                "pre_roll_id": pre_roll.pre_roll_id,
                "cultivator": pre_roll.cultivator,
                "strain": pre_roll.strain,
                "url_path": return_image_url_from_supa_storage(str(Path(pre_roll.card_path))),
                "voting_open": pre_roll.voting_open,
                "is_mystery": pre_roll.is_mystery,
                "description_id": description.description_id,
                "description_text": description.description,
                "effects": description.effects,
                "lineage": description.lineage,
                "terpenes_list": description.terpenes_list,
                "cultivar": description.cultivar_email,
            }
    except Exception as e:
        traceback.print_exc()
        print(f"Error fetching pre roll and description: {e}")
    return None


@settings.retry_db
async def create_preroll_ranking(ranking: PreRollRankingSchema, db: Session):
    ranking_data_dict = ranking.dict()
    try:
        created_ranking = Pre_Roll_Ranking(**ranking_data_dict)
        db.add(created_ranking)
        db.commit()
    except:
        db.rollback()
        raise
    else:
        db.refresh(created_ranking)
    return {"pre_roll_ranking": True}


@settings.retry_db
async def update_or_create_pre_roll_ranking(ranking_dict: PreRollRankingSchema, db: Session):
    existing_ranking = (
        db.query(Pre_Roll_Ranking)
        .filter(
            Pre_Roll_Ranking.cultivator == ranking_dict.cultivator,
            Pre_Roll_Ranking.strain == ranking_dict.strain,
            Pre_Roll_Ranking.connoisseur == ranking_dict.connoisseur,
        )
        .first()
    )

    if existing_ranking:
        for key, value in ranking_dict.dict().items():
            if value is not None:
                setattr(existing_ranking, key, value)
        try:
            db.commit()
            db.refresh(existing_ranking)
            return {"pre_roll_ranking": True}
        except:
            db.rollback()
            raise
    else:
        await create_preroll_ranking(ranking_dict, db)

    return {"pre_roll_ranking": True}


async def get_pre_roll_ranking_data_and_path_from_id(
    db: Session, id_selected: int
) -> Pre_Roll_Ranking:

    ranking = db.query(Pre_Roll_Ranking).filter(Pre_Roll_Ranking.pre_roll_id == id_selected).first()
    ranking_vals = [val for key, val in vars(ranking).items() if key.endswith("rating")]
    overall_score = round(sum(filter(None, ranking_vals)) / (len(ranking_vals)), 2)
    if ranking:
        return {
            "id": ranking.pre_roll_id,
            "strain": ranking.strain,
            "cultivator": ranking.cultivator,
            "overall": overall_score,
            "roll": get_average_of_list(ranking.roll_rating),
            "burn": get_average_of_list(ranking.burn_rating),
            "flavor": get_average_of_list(ranking.flavor_rating),
            "effects": get_average_of_list(ranking.effects_rating),
            "airflow": get_average_of_list(ranking.airflow_rating),
            "tightness": get_average_of_list(ranking.tightness_rating),
            "light": get_average_of_list(ranking.ease_to_light_rating),
        }
    else:
        return {"ranking_id": id_selected, "message": "Ranking not found"}


async def get_all_strains(db: Session) -> List[str]:
    all_strains = db.query(Pre_Roll_Ranking.strain).all()
    return sorted(set([result[0] for result in all_strains]))


async def get_all_strains_for_cultivator(cultivator_selected: str, db: Session) -> List[str]:
    all_strains = (
        db.query(Pre_Roll_Ranking.strain)
        .filter(Pre_Roll_Ranking.cultivator == cultivator_selected)
        .all()
    )
    return sorted([result[0] for result in all_strains])


async def get_all_cultivators(db: Session) -> List[str]:
    all_cultivators = db.query(Pre_Roll_Ranking.cultivator).all()
    return sorted(set([result[0] for result in all_cultivators]))


async def get_all_cultivators_for_strain(strain_selected: str, db: Session) -> List[str]:
    all_cultivators = (
        db.query(Pre_Roll_Ranking.cultivator)
        .filter(Pre_Roll_Ranking.strain == strain_selected)
        .all()
    )
    return sorted(set([result[0] for result in all_cultivators]))


async def get_top_pre_roll_strains(db: Session) -> List[Dict]:
    avg_rankings = (
        db.query(
            Pre_Roll_Ranking.strain,
            Pre_Roll_Ranking.cultivator,
            func.avg(Pre_Roll_Ranking.roll_rating),
            func.avg(Pre_Roll_Ranking.flavor_rating),
            func.avg(Pre_Roll_Ranking.airflow_rating),
            func.avg(Pre_Roll_Ranking.burn_rating),
            func.avg(Pre_Roll_Ranking.effects_rating),
            func.avg(Pre_Roll_Ranking.tightness_rating),
            func.avg(Pre_Roll_Ranking.ease_to_light_rating),
        )
        .filter(Pre_Roll_Ranking.cultivator != "Connoisseur")
        .filter(Pre_Roll_Ranking.strain.ilike("%Test%") == False)
        .group_by(Pre_Roll_Ranking.strain, Pre_Roll_Ranking.cultivator)
        .all()
    )

    scored_strains = []
    for strain in avg_rankings:
        vals_list = strain[2:]
        overall_score = sum(filter(None, vals_list)) / len(strain[2:])
        scored_strains.append((strain[0], strain[1], round(overall_score, 1)))
    scored_strains.sort(key=lambda x: x[2], reverse=True)

    top_strains = scored_strains[:3]
    return_strains = []
    for strain_dict in top_strains:
        pre_roll_data = get_pre_roll_and_description(
            db,
            strain=strain_dict[0],
            cultivator=strain_dict[1],
        )
        if pre_roll_data:
            pre_roll_data["overall_score"] = strain_dict[2]
            return_strains.append(pre_roll_data)

    return return_strains


async def get_pre_roll_ratings_by_id(pre_roll_id: int, db: Session) -> Dict:
    avg_rankings = (
        db.query(
            func.avg(Pre_Roll_Ranking.roll_rating),
            func.avg(Pre_Roll_Ranking.flavor_rating),
            func.avg(Pre_Roll_Ranking.airflow_rating),
            func.avg(Pre_Roll_Ranking.burn_rating),
            func.avg(Pre_Roll_Ranking.effects_rating),
            func.avg(Pre_Roll_Ranking.tightness_rating),
            func.avg(Pre_Roll_Ranking.ease_to_light_rating),
        )
        .filter(Pre_Roll_Ranking.pre_roll_id == pre_roll_id)
        .first()
    )
    if not avg_rankings or any(rating is None for rating in avg_rankings):
        return {"error": "Pre-roll not found or incomplete data"}

    ratings = [rating for rating in avg_rankings if rating is not None]
    if not ratings:
        return {"error": "Incomplete data for the given pre_roll_id"}

    overall_score = sum(ratings) / len(ratings)

    pre_roll_data = {
        "pre_roll_id": pre_roll_id,
        "overall_score": round(overall_score, 2),
        "roll_rating": avg_rankings[0],
        "flavor_rating": avg_rankings[1],
        "airflow_rating": avg_rankings[2],
        "burn_rating": avg_rankings[3],
        "effects_rating": avg_rankings[4],
        "tightness_rating": avg_rankings[5],
        "ease_to_light_rating": avg_rankings[6],
    }

    return pre_roll_data
