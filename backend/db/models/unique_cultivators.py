#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jun  2 10:23:49 2024

@author: dale
"""

from sqlalchemy.orm import relationship
from sqlalchemy import Column, BigInteger, Text, ForeignKey
from db.base_class import Base


class UniqueCultivators(Base):
    __tablename__ = "unique_cultivators"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    cultivator = Column(Text, nullable=False, unique=True, index=True)
    voting = relationship("CultivatorVoting", back_populates="cultivator_info")


class CultivatorVoting(Base):
    __tablename__ = "cultivator_voting"
    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    cultivator_id = Column(
        BigInteger,
        ForeignKey("unique_cultivators.id", onupdate="CASCADE", ondelete="SET NULL"),
    )
    email = Column(
        Text,
        ForeignKey("user.email", onupdate="CASCADE", ondelete="SET NULL"),
        nullable=False,
    )
    cultivator_info = relationship("UniqueCultivators", back_populates="voting")
    voter_info = relationship("User", back_populates="cultivator_voting")
