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
from fastapi import APIRouter, Request, Form, Depends, Query, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List
from route_subscribers import create_subscriber, remove_subscriber
from schemas.subscribers import SubscriberCreate
from db.session import get_db, get_supa_db
from version1._supabase.route_flower_reviews import (
    get_all_strains,
    get_all_cultivators_for_strain,
    return_selected_review,
    add_new_votes_to_flower_strain,
)


templates_dir = Path(
    Path(__file__).parents[2],
    'templates',
)

templates = Jinja2Templates(
    directory=str(templates_dir)
)
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


@general_pages_router.get("/voting-home")
async def voting_home(
    request: Request
):
    return templates.TemplateResponse(
        str(
            Path(
                'general_pages',
                'voting_home.html'
            )
        ),
        {
            "request": request,
        },
    )


@general_pages_router.get("/form", response_class=HTMLResponse)
async def form(
    request: Request
):
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
async def submit_form(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    zip_code: str = Form(...),
    db: Session = Depends(get_db),
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
        'giveaway_subscribers.csv'
    )
    if os.path.exists(str(data_path)):
        df = pd.concat(
            [
                pd.read_csv(
                    str(data_path)
                ).copy(),
                df.copy()
            ],
            axis=0
        )
    # Save to CSV file
    df.to_csv(
        str(data_path),
        index=False
    )
    subscriber_data = SubscriberCreate(email=email)
    create_subscriber(subscriber=subscriber_data, db=db)

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
        'data.csv'
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


@general_pages_router.get("/get-all-strains", response_model=List[str])
async def get_all_strains_route(
        db: Session = Depends(get_supa_db)) -> List[str]:
    return get_all_strains(db)


@general_pages_router.get("/get-cultivators-for-strain", response_model=List[str])
async def get_all_cultivators_for_strain_route(
        strain_selected: str = Query(...),
        db: Session = Depends(get_supa_db)) -> List[str]:
    return get_all_cultivators_for_strain(strain_selected, db)


@general_pages_router.post("/get-review", response_model=List[str])
async def get_flower_review_voting_page(
    request: Request,
    strain_selected: str = Form(...),
    cultivator_selected: str = Form(...),
    db: Session = Depends(get_supa_db),
) -> templates.TemplateResponse:
    review_dict = return_selected_review(
        strain_selected,
        cultivator_selected,
        db=db,
    )
    try:
        request_dict = {
            "request": request,
        }
        response_dict = {**request_dict, **review_dict}
        return templates.TemplateResponse(
            str(
                Path(
                    'general_pages',
                    'voting_home.html'
                )
            ),
            response_dict
        )
    except:
        return templates.TemplateResponse(
            str(
                Path(
                    'general_pages',
                    'voting_home.html'
                )
            ),
            {
                "request": request,
            }
        )


@general_pages_router.get("/{subdomain}.cannabiscult.co")
async def redirect_to_auth_provider(subdomain: str, auth_url: str=None):
    if not auth_url:
        raise HTTPException(status_code=400, detail="auth_provider_url must be provided")
    return RedirectResponse(url=auth_url)


async def get_current_partner_data():
    import get_partner_gsheet.get_gsheet_pandas as get_gsheet
    return get_gsheet._get_deal_workbook_and_return_dict()
