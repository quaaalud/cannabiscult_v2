#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 26 19:23:13 2024

@author: dale
"""

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from urllib.parse import urlencode, urlparse, urlunparse


class LegacyURLMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):

        legacy_strain_mapping = {
            "Citrus 1": ("Vibe", "Mimosa"),
            "Citrus 2": ("Nuthera", "Lemon Bar"),
            "Citrus 3": ("Greenlight", "Goombas"),
            "Citrus 4": ("Local Cannabis", "Purple 43"),
            "LIVE RESIN CP 1": ("Nuthera", "Red Runtz Live Badder"),
            "LIVE RESIN CP 2": ("Vibe", "Liquid Sunshine Live Badder"),
            "LIVE RESIN CP 3": ("Sinse", "Blueberry Muffin Live Badder"),
            "Cult Flower 1": ("Cloud Cover", "Detroit Runtz"),
            "Cult Flower 2": ("Vibe", "Grapes and Cream"),
            "Cult Flower 3": ("Robust", "Government Oasis"),
            "Cult Flower 4": ("Local", "RS11"),
            "Cult Rosin 1": ("Vibe", "Liquid Sunshine"),
            "Cult Rosin 2": ("Robust", "Orange Runtz"),
            "Cult Rosin 3": ("Local", "RS11"),
            "CC 1": ("Notorious", "Piezatti"),
            "CC 2": ("Amaze", "Sub Zero"),
            "CC 3": ("Daybreak", "AF-1"),
            "CC 4": ("Camp", "Biscotti Pie 6"),
            "CC1": ("Illicit", "GMO Cookies"),
            "CC2": ("Sundro", "Super Buff Cherries"),
            "CC3": ("Robust", "Tahiti Lime"),
            "CC4": ("Cloud Cover", "Peach Crescendo"),
            "CultFlower1": ("Nuthera", "Grape Cream Cake"),
            "CultFlower2": ("Vibe", "RKO"),
            "CultFlower3": ("Sinse", "Cap Junky"),
            "CultFlower4": ("C4", "Lemon Drip"),
            "CHAMPIONSHIP CP1": ("Sundro", "Lemon Oreoz"),
            "CHAMPIONSHIP CP2": ("Local", "RS11"),
            "CHAMPIONSHIP CP3": ("Vibe", "Guava Tart"),
            "CHAMPIONSHIP CP4": ("Amaze", "Blue Zushi"),
            "RC 39": ("Amaze", "Blueberry Clementine Live Rosin"),
            "RC 40": ("Vibe", "Grape Sunkist"),
            "RC 41": ("Monopoly Melts", "Grape Sherb"),
            "R1CP1": ("Amaze", "Bull Dance"),
            "R1CP2": ("Camp", "California 10"),
            "R1CP3": ("Illicit", "Chem Butter"),
            "R1CP4": ("Notorious", "Coal Creek Kush"),
        }
        query_params = dict(request.query_params)
        strain_selected = query_params.get("strain_selected")
        if strain_selected in legacy_strain_mapping:
            new_cultivator, new_strain = legacy_strain_mapping[strain_selected]
            query_params["cultivator_selected"] = new_cultivator
            query_params["strain_selected"] = new_strain

            new_query_string = urlencode(query_params)

            url_parts = list(urlparse(str(request.url)))
            url_parts[4] = new_query_string
            new_url = urlunparse(url_parts)

            return Response(status_code=302, headers={"Location": new_url})

        response = await call_next(request)
        return response
