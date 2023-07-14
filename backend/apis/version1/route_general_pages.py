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
from typing import List
from route_subscribers import create_subscriber, remove_subscriber
from schemas.subscribers import SubscriberCreate
from db.session import get_supa_db
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


@general_pages_router.get("/login")
async def login_form(
    request: Request
):
    return templates.TemplateResponse(
        str(
            Path(
                'general_pages',
                'login.html'
            )
        ),
        {
            "request": request,
        }
    )


@general_pages_router.get("/sign-up")
async def signup_form(
    request: Request
):
    return templates.TemplateResponse(
        str(
            Path(
                'general_pages',
                'sign_up.html'
            )
        ),
        {
            "request": request,
        }
    )


@general_pages_router.get("/forgot-password")
async def forgot_password_form(
    request: Request
):
    return templates.TemplateResponse(
        str(
            Path(
                'general_pages',
                'forgot-password.html'
            )
        ),
        {
            "request": request,
        }
    )


@general_pages_router.post("/submit", response_model=None)
async def submit_form(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    zip_code: str = Form(...),
    db: Session = Depends(get_supa_db),
    ) -> templates.TemplateResponse:
  
    subscriber_data = SubscriberCreate(
        email=email,
        name=name,
        zip_code=zip_code,
        phone=phone,
    )
    create_subscriber(subscriber=subscriber_data, db=db)

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
    db: Session = Depends(get_supa_db)
    ) -> templates.TemplateResponse:
  
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
    
    
@general_pages_router.post("/submit-vote", response_model=List[str])
async def submit_flower_review_vote(
    request: Request,
    strain_selected: str = Form(...),
    cultivator_selected: str = Form(...),
    structure_vote: str = Form(...),
    nose_vote: str = Form(...),
    flavor_vote: str = Form(...),
    effects_vote: str = Form(...),
    db: Session = Depends(get_supa_db),
) -> templates.TemplateResponse:
    try:
        review_dict = add_new_votes_to_flower_strain(
            cultivator_selected,
            strain_selected,
            structure_vote,
            nose_vote,
            flavor_vote,
            effects_vote,
            db
        )
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
        raise HTTPException(
            status_code=400, 
            detail="auth_provider_url must be provided"
        )
    return RedirectResponse(url=auth_url)


async def get_current_partner_data():
    import get_partner_gsheet.get_gsheet_pandas as get_gsheet
    return get_gsheet._get_deal_workbook_and_return_dict()
