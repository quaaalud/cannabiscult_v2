#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar  5 21:17:34 2023

@author: dale
"""

import os
import datetime
import sys
from pathlib import Path
from dotenv import load_dotenv
from pydantic import BaseModel
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type
from sqlalchemy.exc import (
    OperationalError,
    DisconnectionError,
    DatabaseError,
    InterfaceError,
)
import socket


load_dotenv()


class Settings:
    PROJECT_NAME: str = "Cannabis Cult"
    PROJECT_VERSION: str = "2.0.0"
    POSTGRES_USER: str = os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD")
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB")
    DATABASE_URL: str = (
        f"postgresql://postgres.{POSTGRES_USER}:{POSTGRES_PASSWORD}@aws-0-us-east-1.pooler.supabase.com:5432/postgres"
    )

    SUPA_ID: str = os.getenv("SUPA_ID")
    SUPA_JWT: str = os.getenv("SUPA_JWT")
    SUPA_PORT: str = os.getenv("SUPA_PORT")
    SUPA_PASSWORD: str = os.getenv("SUPA_PASSWORD")
    SUPA_PRIVATE_KEY: str = os.getenv("SUPA_PRIVATE_KEY")
    SUPA_PUBLIC_KEY: str = os.getenv("SUPABASE_KEY")
    SUPA_STORAGE_URL: str = os.getenv("SUPA_STORAGE_URL")
    SUPA_URL: str = (
        f"postgresql://postgres.{SUPA_ID}:{SUPA_PASSWORD}@aws-0-us-east-1.pooler.supabase.com:{SUPA_PORT}/postgres"
    )
    ALGO: str = os.getenv("ALGO")
    PRIMARY_BUCKET: str = os.getenv("POSTGRES_DB")

    core_dir = Path(__file__).parents[0]
    backend_dir = Path(__file__).parents[1]
    main_dir = Path(__file__).parents[2]
    apis_dir = backend_dir / "apis"
    version_dir = apis_dir / "version1"
    supa_dir = version_dir / "_supabase"

    def __init__(self):
        self.retry_db = self.set_retry()
        self._set_project_paths()

    @staticmethod
    def date_handler(obj):
        if isinstance(obj, datetime.date):
            return obj.isoformat()
        else:
            raise TypeError("Type %s not serializable" % type(obj))

    @classmethod
    def _set_project_paths(cls):
        if str(cls.main_dir) not in sys.path:
            sys.path.append(str(cls.main_dir))

        if str(cls.backend_dir) not in sys.path:
            sys.path.append(str(cls.backend_dir))

        if str(cls.core_dir) not in sys.path:
            sys.path.append(str(cls.core_dir))

        if str(cls.apis_dir) not in sys.path:
            sys.path.append(str(cls.apis_dir))

        if str(cls.version_dir) not in sys.path:
            sys.path.append(str(cls.version_dir))

        if str(cls.supa_dir) not in sys.path:
            sys.path.append(str(cls.supa_dir))

    @staticmethod
    # Retry configuration enhanced for more exceptions
    def set_retry():
        return retry(
            wait=wait_exponential(multiplier=1, min=4, max=10),
            stop=stop_after_attempt(5),
            retry=retry_if_exception_type(
                (
                    OperationalError,
                    DisconnectionError,
                    DatabaseError,
                    InterfaceError,
                    socket.timeout,
                    socket.error,
                )
            ),
        )


class Config(BaseModel):
    SUPA_STORAGE_URL: str
    SUPA_PUBLIC_KEY: str
    ALGO: str
    PRIMARY_BUCKET: str = os.getenv("POSTGRES_DB")


settings = Settings()
