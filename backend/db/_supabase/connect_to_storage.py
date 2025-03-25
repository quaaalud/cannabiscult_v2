#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jul  2 22:54:46 2023

@author: dale
"""

import os
import base64
import tempfile
import mimetypes
from supabase import Client
from db._supabase import supa_client


def delete_temporary_file(temp_file_path: str):
    os.remove(temp_file_path)


def get_reviews_list() -> list[dict]:
    bucket = supa_client.get_cc_bucket()
    folder_path = "reviews"
    return bucket.list(path=folder_path)


def get_image_from_results(file_path: str):
    bucket = supa_client.get_cc_bucket()
    img_bytes = bucket.download(path=file_path)
    return base64.b64encode(img_bytes).decode()


def return_image_url_from_supa_storage(file_path: str):
    file_path = file_path.replace("'", "")
    return supa_client.get_signed_url_from_storage(file_path=file_path)


def _copy_file_in_storage(client: Client, org_bucket: str, new_bucket: str, transfer_file: str, to_transfer_path: str):
    upload_response = None
    download_response = client.storage.from_(org_bucket).download(transfer_file)
    if not download_response:
        raise Exception("Download returned no data.")
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(download_response)
        temp_file_path = tmp.name
    mime_type, _ = mimetypes.guess_type(transfer_file)
    try:
        if not mime_type:
            raise Exception(f"Mime Type Not Determined for {transfer_file}")
        upload_response = client.storage.from_(new_bucket).upload(
            file=temp_file_path,
            path=to_transfer_path,
            file_options={
                "cache-control": "3600",
                "upsert": "false",
                "content-type": mime_type,
            },
        )
    except Exception as e:
        if getattr(e, "status") == "409":
            client.storage.from_(org_bucket).remove(transfer_file)
            pass
        else:
            raise Exception(f"Error processing {transfer_file}: {e}")
    else:
        client.storage.from_(org_bucket).remove(transfer_file)
    finally:
        delete_temporary_file(temp_file_path)
    return upload_response


async def copy_new_primary_to_reviews_directory(
    current_primary: str, new_primary: str, cultivator_name: str, strain_name: str
) -> str:
    client = supa_client.return_created_client()
    old_filename = os.path.basename(current_primary)
    file_name = os.path.basename(new_primary)
    destination_path = f"{os.path.dirname(current_primary)}/{file_name}"
    if "Connoisseur_Pack" in destination_path:
        destination_path = f"reviews/{cultivator_name}/{strain_name}/{file_name}"
    add_img_path = f"{os.path.dirname(new_primary)}/{old_filename}"
    try:
        _copy_file_in_storage(client, "additional_product_images", "cannabiscult", new_primary, destination_path)
        _copy_file_in_storage(client, "cannabiscult", "additional_product_images", current_primary, add_img_path)
        return destination_path
    except Exception as e:
        raise Exception(f"Error copying new primary image to reviews directory: {e}")
