# -*- coding: utf-8 -*-

import tempfile
import shutil
import os
import magic
import requests
import json
from fastapi import (
    APIRouter,
    HTTPException,
    Depends,
    UploadFile,
    File,
    Query,
)
from typing import Dict, Union, Any, Optional
from pydantic import BaseModel, validator
from supabase import Client
from sqlalchemy import select
from sqlalchemy.orm import Session
from core.config import settings
from db.session import get_db
from db.repository.search_class import get_card_path_by_details, RANKING_LOOKUP, product_type_to_model
from db._supabase.connect_to_auth import SupaAuth
from db._supabase.connect_to_storage import return_image_url_from_supa_storage, copy_new_primary_to_reviews_directory


router = APIRouter()


DEFAULT_IMAGE_FILTERS = {
    "nudity": {"none": 0.95},
    "type": {"photo": 0.0, "illustration": 0.0, "ai_generated": 0.7},
    "quality": 0.35,
    "offensive": 0.01,
    "scam": 0.1,
    "violence": 0.01,
    "self-harm": 0.01,
}


class ImagePathRequest(BaseModel):
    product_type: str
    strain: str
    cultivator: str

    class Config:
        from_attributes = True
        populate_by_name = True


class ImageUpload(BaseModel):
    image: Union[UploadFile, None] = None

    @validator("image")
    def validate_image(cls, v):
        if v:
            mime_type = magic.from_buffer(v.file.read(1024), mime=True)
            v.file.seek(0)
            if not mime_type.startswith("image/"):
                raise ValueError("Invalid image file")
        return v


async def _return_supabase_private_client() -> Client:
    supabase = SupaAuth()._client
    return supabase


def is_image_safe(response, filters=DEFAULT_IMAGE_FILTERS):
    if response.get("nudity", {}).get("none", 1) < filters["nudity"]["none"]:
        return False
    type_data = response.get("type", {})
    if type_data.get("photo", 0) < filters["type"]["photo"]:
        return False
    if type_data.get("ai_generated", 1) > filters["type"]["ai_generated"]:
        return False
    if response.get("quality", {}).get("score", 1) < filters["quality"]:
        return False
    if any(val > filters["offensive"] for val in response.get("offensive", {}).values()):
        return False
    if response.get("scam", {}).get("prob", 0) > filters["scam"]:
        return False
    if response.get("violence", {}).get("prob", 0) > filters["violence"]:
        return False
    if response.get("self-harm", {}).get("prob", 0) > filters["self-harm"]:
        return False
    return True


async def check_image_against_default_filters(file_bytes: bytes):
    files = {"media": file_bytes}
    r = requests.post("https://api.sightengine.com/1.0/check.json", files=files, data=settings.SIGHTENGINE_PARAMS)
    output = json.loads(r.text)
    return is_image_safe(output)


async def save_temporary_image_async(file: UploadFile) -> str:
    try:
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            shutil.copyfileobj(file.file, tmp)
            temp_file_path = tmp.name
        return temp_file_path
    finally:
        file.file.close()


def delete_temporary_file(temp_file_path: str):
    os.remove(temp_file_path)


async def update_product_image_url(product_id: str, file_path: str, supabase: Client):
    try:
        image_url = supabase.storage.from_("additional_product_images").get_public_url(file_path)
        updated_product, count = (
            supabase.table("additional_product_images").update({"image_url": image_url}).eq("id", product_id).execute()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def upload_image_to_supabase(
    product_type: str,
    product_id: str,
    file: UploadFile = File(...),
    supabase: Client = Depends(_return_supabase_private_client),
) -> Dict[str, str]:
    if not product_id:
        raise HTTPException(status_code=400, detail="Product ID required")
    storage_str = "additional_product_images"
    image_data = ImageUpload(image=file)
    if not image_data.image:
        raise HTTPException(status_code=400, detail="Invalid image file")
    temp_file_path = await save_temporary_image_async(file)
    dir_list = supabase.storage.from_(storage_str).list(f"{product_type}/{product_id}")
    if "error" in dir_list:
        print(dir_list)
        delete_temporary_file(temp_file_path)
        raise HTTPException(status_code=500, detail=dir_list["error"]["message"])
    file_path = f"{product_type}/{product_id}/{file.filename}"
    try:
        with open(temp_file_path, "rb") as f:
            image_is_safe = await check_image_against_default_filters(f)
            if not image_is_safe:
                return_message = {
                    "message": "Error uploading file: ",
                    "path": str(file.filename),
                    "error": "Image was deemed unsafe or low quality.",
                }
                return return_message
            f.seek(0)
            mime_type = magic.from_buffer(f.read(1024), mime=True)
            f.seek(0)
            supabase.storage.from_(storage_str).upload(file=f, path=file_path, file_options={"content-type": mime_type})
            return {"message": "File uploaded successfully", "path": file_path}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")
    finally:
        delete_temporary_file(temp_file_path)


@router.post("/{product_type}/{product_id}/upload/")
async def upload_product_image(
    product_type: str,
    product_id: str,
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
    return await upload_image_to_supabase(product_type, product_id, file, supabase)


@router.get("/{product_type}/{product_id}/")
async def list_product_images(
    product_type: str,
    product_id: str,
    supabase: Client = Depends(_return_supabase_private_client),
):
    try:
        images = supabase.storage.from_("additional_product_images").list(f"{product_type}/{product_id}")
        if not images:
            return []
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return [
        supabase.storage.from_("additional_product_images").get_public_url(f"{product_type}/{product_id}/{img['name']}")
        for img in images
    ]


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
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    extra_images = {}
    for img in images:
        if "emptyFolderPlaceholder" not in img["name"]:
            extra_img_path = f"{product_type.lower()}/{product_id}/{img['name']}"
            extra_img_url = supabase.storage.from_("additional_product_images").get_public_url(extra_img_path)
            extra_images[extra_img_path] = extra_img_url
    return {product_type.replace("-", "_").lower(): {str(product_id): {**primary_image, **extra_images}}}


async def _return_image_url(card_path: str):
    try:
        return return_image_url_from_supa_storage(card_path)
    except Exception:
        return "https://tahksrvuvfznfytctdsl.supabase.co/storage/v1/object/public/cannabiscult/reviews/Connoisseur_Pack/CP_strains.webp"


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


@router.post("/make_primary", response_model=Dict[str, Any])
async def make_primary_image(
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
