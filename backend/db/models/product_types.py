#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov  5 17:09:03 2023

@author: dale
"""

from sqlalchemy import Column, String, Integer, Float
from sqlalchemy.dialects.postgresql import JSONB
from db.base_class import Base


class Product_Types(Base):
    __table_args__ = {"schema": "public"}

    product_type = Column(String, nullable=False, primary_key=True)
    extra_data = Column(JSONB, nullable=True)


class Terp_Table(Base):
    __tablename__ = 'terp_table'
    row_id = Column(Integer, primary_key=True, autoincrement=True)
    flower_id = Column(Integer, primary_key=True, nullable=True)
    concentrate_id = Column(Integer, primary_key=True, nullable=True)
    pre_roll_id = Column(Integer, primary_key=True, nullable=True)
    edible_id = Column(Integer, primary_key=True, nullable=True)
    strain_type = Column(String, nullable=True)

    alpha_bergamotene = Column(Float)
    alpha_beta_cis_ocimene = Column(Float)
    alpha_beta_pinene = Column(Float)
    alpha_beta_thujene = Column(Float)
    alpha_bisabolene = Column(Float)
    alpha_bisabolol = Column(Float)
    alpha_cedrene = Column(Float)
    alpha_fenchene = Column(Float)
    alpha_humulene = Column(Float)
    alpha_humulene_epoxide_i = Column(Float)
    alpha_phellandrene = Column(Float)
    alpha_pinene = Column(Float)
    alpha_terpinene = Column(Float)
    alpha_terpineol = Column(Float)
    alpha_terpinolene = Column(Float)
    alpha_thujene = Column(Float)
    alpha_zingiberene = Column(Float)
    beta_asarone = Column(Float)
    beta_bisabolene = Column(Float)
    beta_caryophyllene = Column(Float)
    beta_caryophyllene_oxide = Column(Float)
    beta_farnesene = Column(Float)
    beta_myrcene = Column(Float)
    beta_ocimene = Column(Float)
    beta_pinene = Column(Float)
    beta_selinene = Column(Float)
    beta_terpinene = Column(Float)
    camphene = Column(Float)
    caryophyllene = Column(Float)
    caryophyllene_oxide = Column(Float)
    cis_nerolidol = Column(Float)
    cis_beta_ocimene = Column(Float)
    delta_3_carene = Column(Float)
    delta_limonene = Column(Float)
    eucalyptol = Column(Float)
    gamma_terpinene = Column(Float)
    geraniol = Column(Float)
    guaiol = Column(Float)
    isoborneol = Column(Float)
    isopulegol = Column(Float)
    limonene = Column(Float)
    linalool = Column(Float)
    myrcene = Column(Float)
    nerolidol = Column(Float)
    ocimene = Column(Float)
    p_cymene = Column(Float)
    para_cymene = Column(Float)
    phellandrene = Column(Float)
    terpineol = Column(Float)
    terpinolene = Column(Float)
    trans_nerolidol = Column(Float)
    trans_ocimene = Column(Float)
    y_terpinene = Column(Float)
