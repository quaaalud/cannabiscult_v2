# -*- coding: utf-8 -*-

from fastapi import (
    APIRouter,
    HTTPException,
    Depends,
    UploadFile,
    File,
)
from typing import Dict
import tempfile
import shutil
import os
from supabase import Client
from db._supabase.connect_to_auth import SupaAuth
from typing import Union
from pydantic import BaseModel, validator
import magic


router = APIRouter()


async def _return_supabase_private_client() -> Client:
    supabase = SupaAuth()._client
    return supabase


class ImageUpload(BaseModel):
    image: Union[UploadFile, None] = None

    @validator("image")
    def validate_image(cls, v):
        if v:
            mime_type = magic.from_buffer(v.file.read(1024), mime=True)
            v.file.seek(0)  # Reset the file pointer after reading
            if not mime_type.startswith("image/"):
                raise ValueError("Invalid image file")
        return v


def save_temporary_image(file: UploadFile) -> str:
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
            supabase.table("additional_product_images")
            .update({"image_url": image_url})
            .eq("id", product_id)
            .execute()
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
        return
    storage_str = "additional_product_images"
    image_data = ImageUpload(image=file)
    if not image_data.image:
        raise HTTPException(status_code=400, detail="Invalid image file")

    # Save the validated image temporarily
    temp_file_path = save_temporary_image(file)

    # List all files in the specific product directory to determine the new file's index
    dir_list = supabase.storage.from_(storage_str).list()
    if "error" in dir_list:
        raise HTTPException(status_code=500, detail=dir_list["error"]["message"])

    if len(dir_list) > 0 and str(product_type) in [product["name"] for product in dir_list]:
        dir_list = supabase.storage.from_(storage_str).list(path=product_id)

    # Determine the index for the new file
    file_index = len(dir_list)
    # Construct the file path
    file_path = f"{product_type}/{product_id}/{file_index}_{file.filename}"
    try:
        with open(temp_file_path, "rb") as f:
            mime_type = magic.from_buffer(f.read(1024), mime=True)
            upload_response = supabase.storage.from_(storage_str).upload(
                file=f, path=file_path, file_options={"content-type": mime_type}
            )
        if "error" in upload_response.text:
            raise HTTPException(status_code=500, detail=upload_response["error"]["message"])
        return_message = {"message": "File uploaded successfully", "path": file_path}
    except Exception as e:
        return_message = {"message": "Error uploading file", "path": file_path, "error": e}
    finally:
        delete_temporary_file(temp_file_path)
        return return_message


@router.post("/{prodcut_type}/{product_id}/upload/")
async def upload_product_image(
    product_type: str,
    product_id: str,
    file: UploadFile = File(...),
    supabase: Client = Depends(_return_supabase_private_client),
):
    return await upload_image_to_supabase(product_id, file, supabase)


@router.get("/{product_type}/{product_id}/")
async def list_product_images(
    product_type: str, product_id: str, supabase: Client = Depends(_return_supabase_private_client)
):
    try:
        image_urls = supabase.storage.from_(
            "additional_product_images"
        ).list(f"{product_type}/{product_id}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return [img["name"] for img in image_urls]
