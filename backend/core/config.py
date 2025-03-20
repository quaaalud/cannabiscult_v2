#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar  5 21:17:34 2023

@author: dale
"""

import os
import datetime
import sys
import jwt
import sentry_sdk
from fastapi import Request, HTTPException, status
from jwt import ExpiredSignatureError, InvalidTokenError
from uuid import uuid4
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
from posthog import Posthog

load_dotenv()


class PosthogMonitoring:
    _posthog_client: Posthog = None
    _sentry_sdk: sentry_sdk = None

    def __init__(self):
        self.posthog = self._return_posthog_client()
        self._set_sentry_sdk()

    @classmethod
    def _return_posthog_client(cls):
        if not cls._posthog_client:
            cls._posthog_client = Posthog(
                project_api_key=os.getenv("POSTHOG_KEY"),
                host="https://us.i.posthog.com",
                enable_exception_autocapture=True,
                disable_geoip=False,
            )
        return cls._posthog_client

    @classmethod
    def _set_sentry_sdk(cls):
        if not cls._sentry_sdk:
            sentry_sdk.init(
                dsn="https://a5299021dec7811949190fa7bdd78a9f@o4508927465029632.ingest.us.sentry.io/4508927468175360",
                send_default_pii=True,
                traces_sample_rate=1.0,
                profiles_sample_rate=1.0,
            )

    @staticmethod
    def extract_initial_url(request: Request) -> str:
        forwarded_proto = request.headers.get("x-forwarded-proto")
        forwarded_host = request.headers.get("x-forwarded-host")
        if forwarded_proto and forwarded_host:
            scheme = forwarded_proto.split(",")[0].strip()
            host = forwarded_host.split(",")[0].strip()
            path = request.url.path
            query = request.url.query
            url = f"{scheme}://{host}{path}"
            if query:
                url += f"?{query}"
            return url
        else:
            return str(request.url)

    @staticmethod
    def get_supabase_user_id(request: Request, settings) -> str:
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            raise HTTPException(status_code=401, detail="Missing Authorization header")
        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid Authorization header format")
        token = parts[1]
        try:
            unverified_header = jwt.get_unverified_header(token)
            alg = unverified_header.get("alg")
            if alg == "HS256":
                key = settings.SUPA_JWT
            elif alg == "RS256":
                key = settings.SUPA_PUBLIC_KEY
            else:
                return str(uuid4())
            payload = jwt.decode(token, key=key, algorithms=[alg])
            user_id = payload.get("sub")
            if not user_id:
                return str(uuid4())
            return user_id
        except jwt.PyJWTError:
            return str(uuid4())

    @classmethod
    def capture_event_background(
        cls,
        event_name: str,
        request: Request,
        settings,
        **kwargs,
    ):
        user_id = cls.get_supabase_user_id(request, settings)
        properties = {
            "url": str(request.url),
            "user_id": user_id,
            **kwargs,
        }
        settings.monitoring.posthog.capture(user_id=user_id, event=event_name, properties=properties)


class Settings:
    PROJECT_NAME: str = "Cannabis Cult"
    PROJECT_VERSION: str = "2.1.0"
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

    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID")

    SIGHTENGINE_MODELS: str = os.getenv("SIGHTENGINE_MODELS")
    SIGHTENGINE_USER: str = os.getenv("SIGHTENGINE_USER")
    SIGHTENGINE_KEY: str = os.getenv("SIGHTENGINE_KEY")

    SIGHTENGINE_PARAMS = {
      'models': os.getenv("SIGHTENGINE_MODELS"),
      'api_user': os.getenv("SIGHTENGINE_USER"),
      'api_secret': os.getenv("SIGHTENGINE_KEY")
    }

    core_dir = Path(__file__).parents[0]
    backend_dir = Path(__file__).parents[1]
    main_dir = Path(__file__).parents[2]
    apis_dir = backend_dir / "apis"
    version_dir = apis_dir / "version1"
    supa_dir = version_dir / "_supabase"

    monitoring: Posthog = None

    def __init__(self):
        self.retry_db = self.set_retry()
        self._set_project_paths()
        self.posthog = self._return_posthog_monitoring_client()

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

    @classmethod
    def _return_posthog_monitoring_client(cls):
        if not cls.monitoring:
            cls.monitoring = PosthogMonitoring()
        return cls.monitoring.posthog

    @classmethod
    def jwt_auth_dependency(cls, request: Request):
        token = None
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer"):
            token = auth_header.split("Bearer ")[1].strip()
        if not token:
            token = request.cookies.get("my-access-token")
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing or invalid Authorization header"
            )
        try:
            payload = jwt.decode(token, cls.SUPA_JWT, algorithms=["HS256"], audience="authenticated")
            return payload
        except ExpiredSignatureError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
        except InvalidTokenError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


class Config(BaseModel):
    SUPA_STORAGE_URL: str
    SUPA_PUBLIC_KEY: str
    ALGO: str
    PRIMARY_BUCKET: str = os.getenv("POSTGRES_DB")
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID")


settings = Settings()
