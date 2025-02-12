#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 11 19:32:53 2025

@author: dale
"""

from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from itsdangerous import URLSafeTimedSerializer
from core.config import settings


class CSRFMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, secret_key: str = settings.SUPA_PRIVATE_KEY):
        super().__init__(app)
        self.serializer = URLSafeTimedSerializer(secret_key)

    async def dispatch(self, request: Request, call_next):
        if request.method in ("POST", "PUT", "DELETE", "PATCH"):
            csrf_token = request.headers.get("X-CSRF-Token")
            if not csrf_token:
                raise HTTPException(status_code=400, detail="CSRF token missing")
            try:
                self.serializer.loads(csrf_token, max_age=7200)
            except Exception:
                raise HTTPException(
                    status_code=400, detail="Invalid or expired CSRF token"
                )
        response = await call_next(request)
        return response
