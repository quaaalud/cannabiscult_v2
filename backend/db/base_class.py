#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 10 19:08:36 2023

@author: dale
"""

import enum
from typing import Any
from sqlalchemy.ext.declarative import as_declarative, declared_attr


@as_declarative()
class Base:
    id: Any
    __name__: str

    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()


class StrainCategory(str, enum.Enum):
    indica = "indica"
    indica_dominant_hyrbrid = "indica_dominant_hyrbrid"
    hybrid = "hybrid"
    sativa_dominant_hyrbrid = "sativa_dominant_hyrbrid"
    sativa = "sativa"
    cult_pack = "cult_pack"
