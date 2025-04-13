# -*- coding: utf-8 -*-

from fastapi import (
    APIRouter,
    HTTPException,
    Depends,
    UploadFile,
    File,
    Query,
)
from typing import Dict, Any, Optional
from supabase import Client
from storage3.exceptions import StorageApiError
from sqlalchemy import select
from sqlalchemy.orm import Session
from db.session import get_db
from core.config import settings
from db._supabase.connect_to_storage import copy_new_primary_to_reviews_directory
from db.repository.search_class import get_card_path_by_details, RANKING_LOOKUP, product_type_to_model
from db.repository.images import (
    _return_supabase_private_client,
    upload_image_to_supabase,
    _return_image_url,
    ImagePathRequest,
    make_primary_image,
)

router = APIRouter()


@router.post("/{product_type}/{product_id}/upload/", dependencies=[Depends(settings.jwt_auth_dependency)])
async def upload_product_image(
    product_type: str,
    product_id: str,
    is_new_product: Optional[str] = None,
    file: UploadFile = File(...),
    supabase: Client = Depends(_return_supabase_private_client),
):
    if product_type == "flowerSubmission":
        product_type = "flower"
    elif product_type == "concentrateSubmission":
        product_type = "concentrate"
    elif product_type == "pre_rollSubmission":
        product_type = "pre-roll"
    elif product_type == "edibleSubmission":
        product_type = "edible"
    results = await upload_image_to_supabase(product_type, product_id, file, supabase)
    if is_new_product != "new_product":
        return results
    card_path = results.get("path")
    supabase: Client = Depends(_return_supabase_private_client)
    await make_primary_image(product_type, product_id, card_path)
    return results


@router.get("/{product_type}/{product_id}/")
async def list_product_images(
    product_type: str,
    product_id: str,
    supabase: Client = Depends(_return_supabase_private_client),
):
    try:
        images = supabase.storage.from_("additional_product_images").list(f"{product_type}/{product_id}")
    except StorageApiError:
        supabase.auth.refresh_session()
        images = supabase.storage.from_("additional_product_images").list(f"{product_type}/{product_id}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return [
        supabase.storage.from_("additional_product_images").get_public_url(f"{product_type}/{product_id}/{img['name']}")
        for img in images
    ] if images else []


@router.get("/get_all", response_model=Optional[Dict[str, Any]])
async def get_all_product_images_by_product_match(
    product_type: str = Query(None),
    strain: str = Query(None),
    cultivator: str = Query(None),
    supabase: Client = Depends(_return_supabase_private_client),
    db: Session = Depends(get_db),
):
    product_type = product_type.capitalize()
    if product_type == "Pre-roll":
        product_type = "Pre-Roll"
    model_list = product_type_to_model.get(product_type)
    if not model_list:
        raise HTTPException(status_code=404, detail="Product type not found")
    model = model_list[0]
    stmt = select(model).filter(model.strain.ilike(f"%{strain}%"), model.cultivator.ilike(f"%{cultivator}%"))
    result = db.execute(stmt)
    product = result.scalars().first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    lookup = RANKING_LOOKUP.get(product_type.replace("-", "_").lower())
    if not lookup:
        return None
    RankingModel, id_field_name, email_field_name, RankingSchema = lookup
    product_id = getattr(product, id_field_name)
    primary_card_path = getattr(product, "card_path")
    primary_image_url = await _return_image_url(primary_card_path)
    primary_image = {primary_card_path: primary_image_url}
    try:
        images = supabase.storage.from_("additional_product_images").list(f"{product_type}/{product_id}")
        if not images:
            return {product_type.replace("-", "_").lower(): {str(product_id): primary_image}}
    except StorageApiError:
        supabase.auth.refresh_session()
        images = supabase.storage.from_("additional_product_images").list(f"{product_type}/{product_id}")
        if not images:
            return {product_type.replace("-", "_").lower(): {str(product_id): primary_image}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    extra_images = {}
    for img in images:
        if "emptyFolderPlaceholder" not in img["name"]:
            extra_img_path = f"{product_type.lower()}/{product_id}/{img['name']}"
            extra_img_url = supabase.storage.from_("additional_product_images").get_public_url(extra_img_path)
            extra_images[extra_img_path] = extra_img_url
    return {product_type.replace("-", "_").lower(): {str(product_id): {**primary_image, **extra_images}}}


@router.post("/get-image-url", response_model=Dict[str, str])
async def get_image_from_file_path(
    image_request: ImagePathRequest,
    db: Session = Depends(get_db),
    supabase: Client = Depends(_return_supabase_private_client),
) -> Dict[str, str]:
    card_path = await get_card_path_by_details(
        db, image_request.product_type, image_request.strain, image_request.cultivator
    )
    if not card_path:
        return {
            "img_url": "https://tahksrvuvfznfytctdsl.supabase.co/storage/v1/object/public/cannabiscult/reviews/Connoisseur_Pack/CP_strains.webp"
        }
    img_url = await _return_image_url(card_path)
    return {"img_url": img_url}


@router.post("/make_primary", response_model=Dict[str, Any], dependencies=[Depends(settings.jwt_auth_dependency)])
async def make_primary_image_route(
    product_type: str = Query(..., description="Product type, e.g. Flower, Concentrate, Pre-roll"),
    product_id: int = Query(..., description="ID of the product in the database"),
    card_path: str = Query(..., description="The new path to set as the primary image"),
    supabase: Client = Depends(_return_supabase_private_client),
    db: Session = Depends(get_db),
):
    try:
        product_type = product_type.capitalize()
        if product_type == "Pre-roll":
            product_type = "Pre-Roll"
        model_list = product_type_to_model.get(product_type)
        if not model_list:
            raise HTTPException(status_code=404, detail="Product type not found")
        model = model_list[0]
        lookup = RANKING_LOOKUP.get(product_type.replace("-", "_").lower())
        if not lookup:
            raise HTTPException(status_code=404, detail="No ranking lookup found for this product type.")
        RankingModel, id_field_name, email_field_name, RankingSchema = lookup
        stmt = select(model).where(getattr(model, id_field_name) == product_id)
        result = db.execute(stmt)
        product = result.scalars().first()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        current_primary_img = getattr(product, "card_path")
        cultivator_name = getattr(product, "cultivator")
        strain_name = getattr(product, "strain")
        new_save_path = await copy_new_primary_to_reviews_directory(
            current_primary_img, card_path, cultivator_name, strain_name
        )
        setattr(product, "card_path", new_save_path)
        db.commit()
        db.refresh(product)
        return {"detail": "Successfully updated the primary image.", "new_card_path": product.card_path}
    except Exception as e:
        db.rollback()
        raise e
