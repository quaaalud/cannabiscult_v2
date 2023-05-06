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
from fastapi import APIRouter, Request, Form, HTTPException, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from route_subscribers import create_subscriber, remove_subscriber
from schemas.subscribers import SubscriberCreate
from db.session import get_db


templates_dir = Path(
    Path(__file__).parents[2],
    'templates',
)

templates = Jinja2Templates(directory=str(templates_dir))
general_pages_router = APIRouter()


@general_pages_router.get("/")
async def home(
    request: Request
):
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
            "request": request,
            
        }
    )


@general_pages_router.post("/submit", response_model=None)
async def submit_form(request: Request,
                      name: str = Form(...),
                      email: str = Form(...),
                      subject: str = Form(...),
                      message: str = Form(...),
                      db: Session = Depends(get_db),
                      ) -> templates.TemplateResponse:
    # Create DataFrame
    data = {
        'Name': [str(name)],
        'Email': [str(email)],
        'Subject': [str(subject)],
        'Message': [str(message)],
        'Timestamp': [str(datetime.now())]
    }
    df = pd.DataFrame(data)
    data_path = Path(
        '.',
        'backend',
        'db',
        'emails_db',
        'subscribers.csv'
    )
    if os.path.exists(str(data_path)):
        df = pd.concat(
            [
                pd.read_csv(str(data_path)).copy(),
                df.copy()
            ],
            axis=0
        )
        
    # Drop duplicates
    df = df.copy().drop_duplicates(
        subset=[
            'Email', 
            'Message',
        ],
        ignore_index=True,
    )
    
    # Save to CSV file
    df.to_csv(str(data_path), index=False)
    subscriber_data = SubscriberCreate(email=email)
    create_subscriber(subscriber=subscriber_data, db=db)

    # Render success template
    
    return templates.TemplateResponse(
        str(
            Path(
                'components',
                'success.html'
            )
        ),
        {
            "request": request,
            "name": name,
        }
    )


@general_pages_router.get("/privacy-policy")
async def privacy_policy(
    request: Request
):

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
async def terms_and_conditions(
    request: Request
):

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


@general_pages_router.get("/email-form", response_class=HTMLResponse)
async def email_form(request: Request):
    return templates.TemplateResponse(
        str(
            Path(
                'components',
                'email-form.html'
            )
        ),
        {
            "request": request,
        }
    )


@general_pages_router.post("/submit-email", response_model=None)
async def submit_email_form(request: Request,
                            email: str = Form(...),
                            db: Session = Depends(get_db),
                            ) -> templates.TemplateResponse:
    # Create DataFrame
    data = {
        'Name': ['None'],
        'Email': [str(email)],
        'Subject': ['None'],
        'Message': ['None'],
        'Timestamp': [str(datetime.now())]
    }
    df = pd.DataFrame(data)
    data_path = Path(
        '.',
        'backend',
        'db',
        'emails_db',
        'subscribers.csv'
    )
    if os.path.exists(str(data_path)):
        df = pd.concat(
            [
                pd.read_csv(str(data_path)).copy(),
                df.copy()
            ],
            axis=0
        )
        
    # Drop duplicates
    df = df.copy().drop_duplicates(
        subset=[
            'Email', 
            'Message',
        ],
        ignore_index=True,
    )
    df.to_csv(str(data_path), index=False)

    subscriber_data = SubscriberCreate(email=email)
    create_subscriber(subscriber=subscriber_data, db=db)
    
    return templates.TemplateResponse(
        str(
            Path(
                'components',
                'success.html'
            )
        ),
        {
            "request": request,
            "name": email,
        }
    )


@general_pages_router.get("/unsubscribe", response_class=HTMLResponse)
async def unsubscribe(
    request: Request
):
    return templates.TemplateResponse(
        str(
            Path(
                'general_pages',
                'unsubscribe.html'
            )
        ),
        {
            "request": request,
        },
    )


@general_pages_router.post("/unsubscribe-submit", response_model=None)
async def submit_unsubscribe_form(
    request: Request,
    email: str = Form(...),
    db: Session = Depends(get_db)
) -> templates.TemplateResponse:
    data_path = Path(
        '.',
        'backend',
        'db',
        'emails_db',
        'subscribers.csv'
    )
    if os.path.exists(str(data_path)):
        df = pd.read_csv(str(data_path))
        new_df = df.copy()[
            df['Email'].str.casefold() != (str(email).casefold())
        ]
        new_df.to_csv(str(data_path), index=False)
    remove_subscriber(email, db=db)
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


async def get_current_partner_data():
    import get_partner_gsheet.get_gsheet_pandas as get_gsheet
    return get_gsheet._get_deal_workbook_and_return_dict()
