# -*- coding: utf-8 -*-

import base64
import traceback
import datetime
from pathlib import Path
from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import Optional, Any, Dict, List
from db.base import (
    Flower,
    Flower_Description,
    FlowerReview,
    Flower_Ranking,
    Hidden_Flower_Ranking,
    FlowerVoting,
    MysteryFlowerReview,
)
from schemas.flowers import (
    CreateHiddenFlowerRanking,
    CreateFlowerRanking,
    FlowerVoteCreate,
    CreateMysteryFlowerReview,
)
from db._supabase.connect_to_storage import return_image_url_from_supa_storage, get_image_from_results
from core.config import settings


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
                "strain_category": description.strain_category if description.strain_category else "hybrid",
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
            .filter(Flower.flower_id == flower_id, Flower_Description.cultivar_email == cultivar_email)
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
                "strain_category": description.strain_category if description.strain_category else "hybrid",
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


def get_all_strains(db: Session) -> List[str]:
    all_strains = db.query(FlowerReview.strain).all()
    return sorted(set([result[0] for result in all_strains]))


def get_all_strains_for_cultivator(cultivator_selected: str, db: Session) -> List[str]:
    all_strains = db.query(FlowerReview.strain).filter(FlowerReview.cultivator == cultivator_selected).all()
    return sorted([result[0] for result in all_strains])


def get_all_cultivators(db: Session) -> List[str]:
    all_cultivators = db.query(FlowerReview.cultivator).all()
    return sorted(set([result[0] for result in all_cultivators]))


def get_all_cultivators_for_strain(strain_selected: str, db: Session) -> List[str]:
    all_cultivators = db.query(FlowerReview.cultivator).filter(FlowerReview.strain == strain_selected).all()
    return sorted(set([result[0] for result in all_cultivators]))


def get_review_data_and_path(db: Session, cultivator_select: str, strain_select: str) -> FlowerReview:
    review = (
        db.query(Flower_Ranking)
        .filter((Flower_Ranking.cultivator == cultivator_select) & (Flower_Ranking.strain == strain_select))
        .all()
    )
    if review:
        img_path = str(Path(review.card_path))
        results_bytes = get_image_from_results(img_path)
        struct_avg = get_average_of_list(review.structure)
        nose_avg = get_average_of_list(review.nose)
        flavor_avg = get_average_of_list(review.flavor)
        effects_avg = get_average_of_list(review.effects)
        total_avg = get_average_of_list([struct_avg, nose_avg, flavor_avg, effects_avg])
        return {
            "id": review.id,
            "strain": review.strain,
            "cultivator": review.cultivator,
            "overall": total_avg,
            "structure": struct_avg,
            "nose": nose_avg,
            "flavor": flavor_avg,
            "effects": effects_avg,
            "vote_count": review.vote_count,
            "card_path": results_bytes,
            "terpene_list": review.terpene_list,
            "url_path": return_image_url_from_supa_storage(img_path),
        }
    else:
        return {"strain": strain_select, "message": "Review not found"}


def get_average_of_list(_list_of_floats: list[float]) -> float:
    return round(sum(_list_of_floats) / len(_list_of_floats) * 2) / 2


def get_review_data_and_path_from_id(db: Session, id_selected: int) -> FlowerReview:
    review = db.query(FlowerReview).filter(FlowerReview.id == id_selected).first()
    if review:
        results_bytes = get_image_from_results(str(Path(review.card_path)))
        return {
            "id": review.id,
            "strain": review.strain,
            "cultivator": review.cultivator,
            "overall": review.overall,
            "structure": get_average_of_list(review.structure),
            "nose": get_average_of_list(review.nose),
            "flavor": get_average_of_list(review.flavor),
            "effects": get_average_of_list(review.effects),
            "vote_count": review.vote_count,
            "card_path": results_bytes,
            "url_path": return_image_url_from_supa_storage(str(Path(review.card_path))),
        }
    else:
        return {"review_id": id_selected, "message": "Review not found"}


def append_votes_to_arrays(
    cultivator_select: str,
    strain_select: str,
    structure_value: int,
    nose_value: int,
    flavor_value: int,
    effects_value: int,
    db: Session,
):
    review = (
        db.query(FlowerReview)
        .filter((FlowerReview.strain == strain_select) & (FlowerReview.cultivator == cultivator_select))
        .first()
    )
    if review:
        review.structure = func.array_append(FlowerReview.structure, structure_value)
        review.nose = func.array_append(FlowerReview.nose, nose_value)
        review.flavor = func.array_append(FlowerReview.flavor, flavor_value)
        review.effects = func.array_append(FlowerReview.effects, effects_value)
        review.vote_count = FlowerReview.vote_count + 1
        try:
            db.flush()
            db.commit()
            db.refresh(review)
            results_bytes = get_image_from_results(str(Path(review.card_path)))
            return {
                "id": review.id,
                "strain": review.strain,
                "cultivator": review.cultivator,
                "overall": review.overall,
                "structure": get_average_of_list(review.structure),
                "nose": get_average_of_list(review.nose),
                "flavor": get_average_of_list(review.flavor),
                "effects": get_average_of_list(review.effects),
                "vote_count": review.vote_count,
                "card_path": results_bytes,
            }
        except Exception as e:
            db.rollback()
            print(f"Error: {e}")
            return {"strain": strain_select, "message": "Failed to append values"}
    else:
        return {"strain": strain_select, "message": "Review not found"}


def calculate_overall_score(
    structure_val: float,
    nose_val: float,
    flavor_val: float,
    effects_val: float,
):
    values_list = [structure_val, nose_val, flavor_val, effects_val]
    return get_average_of_list(values_list)


def convert_img_bytes_for_html(img_bytes):
    return base64.b64encode(img_bytes).decode()


def return_selected_review(strain_selected: str, cultivator_selected: str, db: Session):
    return get_review_data_and_path(
        db,
        cultivator_selected,
        strain_selected,
    )


def return_selected_review_by_id(selected_id: str, db: Session):
    return get_review_data_and_path_from_id(db, selected_id)


def add_new_votes_to_flower_values(
    cultivator_select: str,
    strain_select: str,
    structure_vote: int,
    nose_vote: int,
    flavor_vote: int,
    effects_vote: int,
    db: Session,
):
    try:
        return append_votes_to_arrays(
            cultivator_select,
            strain_select,
            structure_vote,
            nose_vote,
            flavor_vote,
            effects_vote,
            db,
        )
    except Exception:
        pass


@settings.retry_db
def create_flower_ranking(ranking_dict: CreateFlowerRanking, db: Session):
    ranking_data_dict = ranking_dict.dict()
    created_ranking = Flower_Ranking(**ranking_data_dict)
    try:
        db.add(created_ranking)
    except Exception:
        db.rollback()
    else:
        db.commit()
        db.refresh(created_ranking)
    finally:
        return created_ranking


@settings.retry_db
def update_or_create_flower_ranking(ranking_dict: CreateFlowerRanking, db: Session):
    existing_ranking = (
        db.query(Flower_Ranking)
        .filter(
            Flower_Ranking.cultivator == ranking_dict.cultivator,
            Flower_Ranking.strain == ranking_dict.strain,
            Flower_Ranking.connoisseur == ranking_dict.connoisseur,
        )
        .first()
    )
    if existing_ranking:
        for key, value in ranking_dict.dict().items():
            setattr(existing_ranking, key, value)
        try:
            db.commit()
            db.refresh(existing_ranking)
            return existing_ranking
        except Exception:
            db.rollback()
            raise
    else:
        # Create a new ranking record
        return create_flower_ranking(ranking_dict, db)


@settings.retry_db
def create_hidden_flower_ranking(ranking_dict: CreateHiddenFlowerRanking, db: Session):
    ranking_data_dict = ranking_dict.dict()
    created_ranking = Hidden_Flower_Ranking(**ranking_data_dict)
    try:
        db.add(created_ranking)
    except Exception:
        db.rollback()
    else:
        db.commit()
        db.refresh(created_ranking)
    finally:
        return created_ranking


def add_new_flower_vote(flower_vote: FlowerVoteCreate, db: Session):
    flower_vote = FlowerVoting(
        created_at=settings.date_handler(datetime.datetime.now()),
        cultivator_selected=str(flower_vote.cultivator_selected),
        strain_selected=str(flower_vote.strain_selected),
        structure_vote=float(flower_vote.structure_vote),
        structure_explanation=str(flower_vote.structure_explanation),
        nose_vote=float(flower_vote.nose_vote),
        nose_explanation=str(flower_vote.nose_explanation),
        flavor_vote=float(flower_vote.flavor_vote),
        flavor_explanation=str(flower_vote.flavor_explanation),
        effects_vote=float(flower_vote.effects_vote),
        effects_explanation=str(flower_vote.effects_explanation),
        user_email=str(flower_vote.user_email),
    )
    try:
        db.add(flower_vote)
        db.commit()
    except Exception:
        db.rollback()
    else:
        db.refresh(flower_vote)
        return flower_vote


def update_or_add_flower_vote(flower_vote: FlowerVoteCreate, db: Session):
    existing_vote = (
        db.query(FlowerVoting)
        .filter(
            FlowerVoting.cultivator_selected == flower_vote.cultivator_selected,
            FlowerVoting.strain_selected == flower_vote.strain_selected,
            FlowerVoting.user_email == flower_vote.user_email,
        )
        .first()
    )
    if existing_vote:
        # Update existing record
        existing_vote.structure_vote = float(flower_vote.structure_vote)
        existing_vote.structure_explanation = str(flower_vote.structure_explanation)
        existing_vote.nose_vote = float(flower_vote.nose_vote)
        existing_vote.nose_explanation = str(flower_vote.nose_explanation)
        existing_vote.flavor_vote = float(flower_vote.flavor_vote)
        existing_vote.flavor_explanation = str(flower_vote.flavor_explanation)
        existing_vote.effects_vote = float(flower_vote.effects_vote)
        existing_vote.effects_explanation = str(flower_vote.effects_explanation)
        existing_vote.created_at = settings.date_handler(datetime.datetime.now())
        try:
            db.commit()
            db.refresh(existing_vote)
            return existing_vote
        except Exception as e:
            db.rollback()
            raise e
    else:
        return add_new_flower_vote(flower_vote, db)


def create_mystery_flower_review(mystery_flower_review: CreateMysteryFlowerReview, db: Session):
    review_data_dict = mystery_flower_review.dict()
    created_mystery_review = MysteryFlowerReview(**review_data_dict)
    try:
        db.add(created_mystery_review)
        db.commit()
    except Exception as e:
        db.rollback()
    else:
        db.refresh(created_mystery_review)
    finally:
        return created_mystery_review
