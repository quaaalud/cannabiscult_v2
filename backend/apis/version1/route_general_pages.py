#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar  5 21:10:59 2023

@author: dale
"""

import os
import pandas as pd
from datetime import datetime
from pathlib import Path
from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates


templates_dir = Path(
    Path(__file__).parents[2],
    'templates',
)

templates = Jinja2Templates(directory=str(templates_dir))
general_pages_router = APIRouter()


@general_pages_router.get("/")
async def home(request: Request):
    partner_data = await get_current_partner_data()
    return templates.TemplateResponse(
        str(
            Path(
                'general_pages', 
                'homepage.html'
            )
        ), 
        {
            "request": request,
            "dispensaries": partner_data,
        },
    )


@general_pages_router.get("/form", response_class=HTMLResponse)
async def form(request: Request):
    return templates.TemplateResponse(
        str(
            Path(
                'components',
                'form.html'
            )
        ),
        {
            "request": request
        }
    )


@general_pages_router.post("/submit", response_model=None)
async def submit_form(request: Request,
                      name: str = Form(...),
                      email: str = Form(...),
                      phone: str = Form(...),
                      zip_code: str = Form(...)
                      ) -> templates.TemplateResponse:
    # Create DataFrame
    data = {
        'Name': [name],
        'Email': [email],
        'Phone': [phone],
        'Zip Code': [zip_code],
        'Timestamp': [str(datetime.now())]
    }
    df = pd.DataFrame(data)
    data_path = Path(
        '.',
        'backend',
        'db',
        'emails_db',
        'data.csv'
    )
    if os.path.exists(str(data_path)):
        df = pd.concat(
            [
                pd.read_csv(str(data_path)).copy(),
                df.copy()
            ],
            axis=0
        )
    # Save to CSV file
    df.to_csv(str(data_path), index=False)

    # Render success template
    return templates.TemplateResponse(
        str(
            Path(
                'general_pages',
                'success.html'
            )
        ),
        {
            "request": request,
            "name": name,
            "email": email,
            "phone": phone,
            "zip_code": zip_code,
        }
    )   

@general_pages_router.get("/privacy-policy")
async def privacy_policy(request: Request):
    
    return templates.TemplateResponse(
        str(
            Path(
                'general_pages', 
                'privacy_policy.html'
            )
        ), 
        {
            "request": request,
        },
    )    
    

@general_pages_router.get("/terms-of-use")
async def terms_and_conditions(request: Request):
    
    return templates.TemplateResponse(
        str(
            Path(
                'general_pages', 
                'terms_and_conditions.html'
            )
        ), 
        {
            "request": request,
        },
    )  
    

async def get_current_partner_data():
    import get_partner_gsheet.get_gsheet_pandas as get_gsheet
    return get_gsheet._get_deal_workbook_and_return_dict()
    
    
    
    
    
    
    
    
    
    