#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 26 19:23:13 2024

@author: dale
"""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from urllib.parse import urlencode


class LegacyURLMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):

        legacy_strain_mapping = {
            "Citrus 1": ("Vibe", "Mimosa"),
            "Citrus 2": ("Nuthera", "Lemon Bar"),
            "Citrus 3": ("Greenlight", "Goombas"),
            "Citrus 4": ("Local Cannabis", "Purple 43"),
        }

        # Extract query parameters
        query_params = dict(request.query_params)

        strain_selected = query_params.get("strain_selected")

        # Check and replace old strain values with new ones, updating cultivator if necessary
        if strain_selected in legacy_strain_mapping:
            new_cultivator, new_strain = legacy_strain_mapping[strain_selected]
            query_params["cultivator_selected"] = new_cultivator
            query_params["strain_selected"] = new_strain

        # Reconstruct the query string from the updated dictionary
        new_query_string = urlencode(query_params)

        # Update the scope with the new query string
        request.scope["query_string"] = new_query_string.encode("utf-8")

        # Proceed to the next middleware or route handler
        response = await call_next(request)
        return response