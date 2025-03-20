#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar  5 21:10:59 2023
@author: dale
"""


from pathlib import Path
from fastapi import APIRouter, Request, Form, Depends, Query, HTTPException, BackgroundTasks
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional, Dict
from db.session import get_db
from core.config import settings, Config
from db.repository import edibles as edibles_repo
from db.repository import pre_rolls
from db.repository.concentrates import get_concentrate_data_and_path
from schemas.mystery_voters import MysteryVoterCreate
from version1._supabase.route_flowers import get_flower_and_description
from version1._supabase import route_concentrates
from version1._supabase.route_mystery_voters import (
    get_voter_info_by_email,
    create_mystery_voter,
)
from route_subscribers import remove_subscriber
from route_users import (
    get_current_users_email,
    async_get_current_users_email,
)


templates_dir = Path(
    Path(__file__).parents[2],
    "templates",
)

templates = Jinja2Templates(directory=str(templates_dir))
general_pages_router = APIRouter()


async def get_config_obj():
    return Config(
        SUPA_STORAGE_URL=settings.SUPA_STORAGE_URL,
        SUPA_PUBLIC_KEY=settings.SUPA_PUBLIC_KEY,
        ALGO=settings.ALGO,
    )


@general_pages_router.get("/", response_class=HTMLResponse)
async def home(request: Request, background_tasks: BackgroundTasks = BackgroundTasks()):
    user_is_logged_in = await async_get_current_users_email() is not None
    background_tasks.add_task(
        settings.monitoring.capture_event_background,
        "landing_page_loaded",
        request,
        settings,
        user_is_logged_in=user_is_logged_in,
    )
    return templates.TemplateResponse(
        str(Path("general_pages", "homepage.html")),
        {
            "request": request,
            "user_is_logged_in": user_is_logged_in,
        },
    )


@general_pages_router.get("/voting-home", response_class=HTMLResponse)
async def voting_home(request: Request):
    user_is_logged_in = await async_get_current_users_email() is not None
    return templates.TemplateResponse(
        str(Path("general_pages", "voting-home.html")),
        {
            "request": request,
            "user_is_logged_in": user_is_logged_in,
        },
    )


@general_pages_router.get("/search", response_class=HTMLResponse)
async def search_page_route(request: Request):
    user_is_logged_in = await async_get_current_users_email() is not None
    return templates.TemplateResponse(
        str(Path("general_pages", "search.html")),
        {
            "request": request,
            "user_is_logged_in": user_is_logged_in,
        },
    )


@general_pages_router.get("/home", response_class=HTMLResponse)
async def user_home(request: Request):
    user_is_logged_in = await async_get_current_users_email() is not None
    return templates.TemplateResponse(
        str(Path("general_pages", "strain_submissions.html")),
        {
            "request": request,
            "user_is_logged_in": user_is_logged_in,
        },
    )


@general_pages_router.get("/forgot-password", response_class=HTMLResponse)
async def forgot_password_landing_page(request: Request):
    user_is_logged_in = await async_get_current_users_email() is not None
    return templates.TemplateResponse(
        str(Path("general_pages", "auth", "forgot_password.html")),
        {
            "request": request,
            "user_is_logged_in": user_is_logged_in,
        },
    )


@general_pages_router.get("/register_success", response_class=HTMLResponse)
async def registration_success_transition_page(request: Request):
    return templates.TemplateResponse(
        str(Path("general_pages", "auth", "register_success.html")),
        {
            "request": request,
        },
    )


@general_pages_router.get("/auth/callback", response_class=HTMLResponse)
async def get_auth_callback_page(request: Request):
    return templates.TemplateResponse(
        str(Path("general_pages", "auth", "auth_callback.html")),
        {
            "request": request,
        },
    )


@general_pages_router.get("/privacy-policy", response_class=HTMLResponse)
async def privacy_policy(request: Request):
    user_is_logged_in = get_current_users_email() is not None
    return templates.TemplateResponse(
        str(Path("general_pages", "privacy_policy.html")),
        {
            "request": request,
            "user_is_logged_in": user_is_logged_in,
        },
    )


@general_pages_router.get("/terms-of-use", response_class=HTMLResponse)
async def terms_and_conditions(request: Request):
    user_is_logged_in = get_current_users_email() is not None
    return templates.TemplateResponse(
        str(Path("general_pages", "terms_and_conditions.html")),
        {
            "request": request,
            "user_is_logged_in": user_is_logged_in,
        },
    )


@general_pages_router.post("/unsubscribe-submit", response_class=HTMLResponse)
async def submit_unsubscribe_form(request: Request, email: str = Form(...), db: Session = Depends(get_db)):
    remove_subscriber(email, db=db)
    return templates.TemplateResponse(
        str(Path("general_pages", "homepage.html")),
        {"request": request},
    )


async def process_flower_request(
    request: Request,
    strain_selected: str,
    cultivator_selected: str,
    cultivar_email: str,
    db: Session,
):
    review_dict = await get_flower_and_description(
        db=db,
        strain=strain_selected,
        cultivator=cultivator_selected,
        cultivar_email=cultivar_email,
    )
    try:
        request_dict = {
            "request": request,
            "user_is_logged_in": get_current_users_email() is not None,
        }
        response_dict = {**request_dict, **review_dict}

        return templates.TemplateResponse(
            str(Path("general_pages", "ranking_pages", "connoisseur_flowers.html")), response_dict
        )
    except Exception:
        return templates.TemplateResponse(
            str(Path("general_pages", "search.html")),
            {
                "request": request,
            },
        )


@general_pages_router.post("/get-review", response_class=HTMLResponse)
async def handle_flower_review_get(
    request: Request,
    *,
    strain_selected: str = Form(None),
    cultivator_selected: str = Form(None),
    cultivar_email: str = Form("aaron.childs@thesocialoutfitus.com"),
    product_type_selected_selected: str = Form("flower"),
    db: Session = Depends(get_db),
):
    return await process_flower_request(request, strain_selected, cultivator_selected, cultivar_email, db)


@general_pages_router.get("/get-review", response_class=HTMLResponse)
async def handle_flower_review_post(
    request: Request,
    *,
    strain_selected: str = Query(None, alias="strain_selected"),
    cultivator_selected: str = Query(None, alias="cultivator_selected"),
    cultivar_email: str = Query("aaron.childs@thesocialoutfitus.com", alias="cultivar_email"),
    product_type_selected: str = Query("flower", alias="product_type_selected"),
    db: Session = Depends(get_db),
):
    return await process_flower_request(request, strain_selected, cultivator_selected, cultivar_email, db)


# Pre-Roll Review and Voting Pages
async def process_pre_roll_request(
    request: Request, strain_selected: str, cultivator_selected: str, cultivar_email: str, db: Session
):
    try:
        user_is_logged_in = get_current_users_email() is not None
        review_dict = await pre_rolls.get_pre_roll_and_description(
            db=db, strain=strain_selected, cultivar_email=cultivar_email, cultivator=cultivator_selected
        )
        request_dict = {
            "request": request,
            "user_is_logged_in": user_is_logged_in,
        }
        response_dict = {**request_dict, **review_dict}
        return templates.TemplateResponse(
            str(Path("general_pages", "ranking_pages", "connoisseur_pre_rolls.html")), response_dict
        )
    except Exception:
        return templates.TemplateResponse(str(Path("general_pages", "voting-home.html")), {"request": request})


@general_pages_router.post("/pre-roll-get-review", response_class=HTMLResponse)
async def handle_pre_roll_review_get(
    request: Request,
    *,
    strain_selected: str = Form(None),
    cultivator_selected: str = Form(None),
    cultivar_email: str = Form("aaron.childs@thesocialoutfitus.com"),
    product_type_selected_selected: str = Form("pre-roll"),
    db: Session = Depends(get_db),
):
    return await process_pre_roll_request(request, strain_selected, cultivator_selected, db)


@general_pages_router.get("/pre-roll-get-review", response_class=HTMLResponse)
async def handle_pre_roll_review_post(
    request: Request,
    *,
    strain: str = Query(None, alias="strain_selected"),
    cultivator: str = Query(None, alias="cultivator_selected"),
    cultivar_email: str = Query("aaron.childs@thesocialoutfitus.com"),
    product_type_selected: str = Query("pre-roll"),
    db: Session = Depends(get_db),
):
    return await process_pre_roll_request(request, strain, cultivator, cultivar_email, db)


@general_pages_router.get("/vibe-hash-hole", response_class=HTMLResponse)
async def vibe_hash_hole_route(request: Request, db: Session = Depends(get_db)):
    cultivator = "Vibe"
    strain = "Hash Hole"
    try:
        return await process_pre_roll_request(request, strain, cultivator, "aaron.childs@thesocialoutfitus.com", db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Edible Review and Voting Pages
async def process_edible_request(
    request: Request, strain_selected: str, cultivator_selected: str, cultivar_email: str, db: Session
):
    try:
        user_is_logged_in = get_current_users_email() is not None
        review_dict = await edibles_repo.get_edible_and_description(
            db=db, strain=strain_selected, cultivar_email=cultivar_email, cultivator=cultivator_selected
        )
        request_dict = {
            "request": request,
            "user_is_logged_in": user_is_logged_in,
        }
        response_dict = {**request_dict, **review_dict}
        return templates.TemplateResponse(
            str(Path("general_pages", "ranking_pages", "connoisseur_edibles.html")), response_dict
        )
    except Exception:
        return templates.TemplateResponse(str(Path("general_pages", "voting-home.html")), {"request": request})


@general_pages_router.post("/edible-get-review", response_class=HTMLResponse)
async def handle_edible_review_get(
    request: Request,
    *,
    strain_selected: str = Form(None),
    cultivator_selected: str = Form(None),
    cultivar_email: str = Form("aaron.childs@thesocialoutfitus.com"),
    product_type_selected_selected: str = Form("edible"),
    db: Session = Depends(get_db),
):
    return await process_edible_request(request, strain_selected, cultivator_selected, db)


@general_pages_router.get("/edible-get-review", response_class=HTMLResponse)
async def handle_edible_review_post(
    request: Request,
    *,
    strain: str = Query(None, alias="strain_selected"),
    cultivator: str = Query(None, alias="cultivator_selected"),
    cultivar_email: str = Query("aaron.childs@thesocialoutfitus.com"),
    product_type_selected: str = Query("edible"),
    db: Session = Depends(get_db),
):
    return await process_edible_request(request, strain, cultivator, cultivar_email, db)


@general_pages_router.get("/get-vibe-edible", response_class=HTMLResponse)
async def handle_vibe_edible_post(
    request: Request,
    edible_strain: str = Query(None, alias="edible_strain"),
    product_type_selected: str = Query(None, alias="product_type_selected"),
    cultivator_selected: str = Query(None, alias="cultivator_selected"),
    strain_selected: str = Query(None, alias="strain_selected"),
    db: Session = Depends(get_db),
):
    strain_to_use = strain_selected if strain_selected else edible_strain

    edible_dict = edibles_repo.get_vibe_edible_data_by_strain(
        db,
        edible_strain=strain_to_use,
    )
    response_dict = {"request": request, **edible_dict}
    return templates.TemplateResponse(
        str(Path("general_pages", "ranking_pages", "vibe-edible-ratings.html")), response_dict
    )


@general_pages_router.get("/vibe_concentrate_ratings", response_class=HTMLResponse)
async def vibe_concentrates_main_page(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse(
        str(Path("general_pages", "ranking_pages", "vibe-concentrate-ratings.html")), {"request": request}
    )


@general_pages_router.get("/get_vibe_concentrate", response_class=HTMLResponse)
async def handle_vibe_concentrate_post(
    request: Request,
    strain: str = Query(None, alias="strain"),
    db: Session = Depends(get_db),
):
    concentrate_dict = get_concentrate_data_and_path(
        db,
        strain=strain,
    )
    response_dict = {"request": request, **concentrate_dict}
    return templates.TemplateResponse(
        str(Path("general_pages", "ranking_pages", "vibe-concentrate-ratings.html")), response_dict
    )


async def process_concentrate_request(
    request: Request,
    strain_selected: str,
    cultivator_selected: str,
    cultivar_email: str,
    db: Session,
):
    try:
        strain_dict = await route_concentrates.get_concentrate_by_strain_and_cultivator(
            strain=strain_selected, cultivator=cultivator_selected, db=db
        )
        if not strain_dict:
            return templates.TemplateResponse(str(Path("general_pages", "voting-home.html")), {"request": request})
        request_dict = {"request": request}
        response_dict = {**request_dict, **strain_dict}
        if not response_dict.get("is_mystery") is True:
            review_dict = await route_concentrates.get_concentrate_and_description(
                db=db,
                strain=strain_selected,
                cultivator=cultivator_selected,
                cultivar_email=cultivar_email,
            )
            response_dict = {**request_dict, **review_dict}
        return templates.TemplateResponse(
            str(Path("general_pages", "ranking_pages", "connoisseur_concentrates.html")), response_dict
        )
    except Exception:
        return templates.TemplateResponse(
            str(Path("general_pages", "voting-home.html")),
            {
                "request": request,
            },
        )


@general_pages_router.post("/concentrate-get-review", response_class=HTMLResponse)
async def handle_concentrate_review_get(
    request: Request,
    *,
    strain_selected: str = Form(None),
    cultivator_selected: str = Form(None),
    product_type_selected: str = Form("concentrate"),
    cultivar_email: str = Form("aaron.childs@thesocialoutfitus.com"),
    db: Session = Depends(get_db),
):
    return await process_concentrate_request(request, strain_selected, cultivator_selected, cultivar_email, db)


@general_pages_router.get("/concentrate-get-review", response_class=HTMLResponse)
async def handle_concentrate_review_post(
    request: Request,
    *,
    strain_selected: str = Query(None, alias="strain_selected"),
    cultivator_selected: str = Query(None, alias="cultivator_selected"),
    product_type_selected: str = Query("concentrate", alias="product_type_selected"),
    cultivar_email: str = Query("aaron.childs@thesocialoutfitus.com", alias="cultivar_email"),
    db: Session = Depends(get_db),
):
    return await process_concentrate_request(request, strain_selected, cultivator_selected, cultivar_email, db)


@general_pages_router.get("/check-mystery-voter")
def check_mystery_voter_email_by_get(
    voter_email: str = Query(None, alias="voter_email"), db: Session = Depends(get_db)
) -> Optional[Dict[str, bool]]:
    voter = get_voter_info_by_email(voter_email=voter_email.lower(), db=db)
    if not voter:
        return {"exists": False}
    return {"exists": True}


@general_pages_router.post("/submit-new-voter", response_model=Dict[str, bool])
async def submit_mystery_voter_create(
    voter_name: str = Form(None),
    voter_email: str = Form(...),
    voter_phone: str = Form(None),
    voter_zip_code: str = Form(None),
    voter_industry_employer: str = Form(None),
    voter_industry_job_title: str = Form(None),
    db: Session = Depends(get_db),
) -> Optional[bool]:
    existing_voter = get_voter_info_by_email(voter_email, db)

    if existing_voter:
        return {"status": True}
    try:
        voter = MysteryVoterCreate(
            email=voter_email.lower(),
            name=voter_name,
            zip_code=voter_zip_code,
            phone=voter_phone,
            industry_employer=voter_industry_employer,
            industry_job_title=voter_industry_job_title,
        )
        create_mystery_voter(voter=voter, db=db)
        return {"status": True}
    except Exception:
        return {"status": False}


@general_pages_router.get("/config")
async def get_config():
    return Config(
        SUPA_STORAGE_URL=settings.SUPA_STORAGE_URL,
        SUPA_PUBLIC_KEY=settings.SUPA_PUBLIC_KEY,
        ALGO=settings.ALGO,
        PRIMARY_BUCKET=settings.PRIMARY_BUCKET,
    )


@general_pages_router.get("/{subdomain}.cannabiscult.co")
async def redirect_to_auth_provider(subdomain: str, auth_url: str = None):
    if not auth_url:
        raise HTTPException(status_code=400, detail="auth_provider_url must be provided")
    return RedirectResponse(url=auth_url)


@general_pages_router.get("/sitemap.xml")
async def sitemap(request: Request):
    return templates.TemplateResponse(
        str(Path("general_pages", "sitemap.xml")),
        {
            "request": request,
        },
    )


@general_pages_router.get("/test_pages/glb_test", response_class=HTMLResponse)
async def glp_test_page(request: Request):
    user_is_logged_in = await async_get_current_users_email() is not None

    return templates.TemplateResponse(
        str(Path("general_pages", "test_pages", "glp_test.html")),
        {
            "request": request,
            "user_is_logged_in": user_is_logged_in,
        },
    )


@general_pages_router.get("/rosin-championship-2025", response_class=HTMLResponse)
async def rosin_championship_2025_landing_route(request: Request):
    user_is_logged_in = await async_get_current_users_email() is not None
    config = await get_config_obj()
    return templates.TemplateResponse(
        str(Path("general_pages", "pack_transition_pages", "rosin-championship-2025.html")),
        {
            "request": request,
            "user_is_logged_in": user_is_logged_in,
            "SUPA_URL": config.SUPA_STORAGE_URL,
            "PUB_KEY": config.SUPA_PUBLIC_KEY,
        },
    )


@general_pages_router.get("/moluv-headstash-bowl", response_class=HTMLResponse)
async def moluv_cult_collab_route(request: Request):
    return templates.TemplateResponse(
        str(Path("general_pages", "pack_transition_pages", "moluv-cult-collab.html")),
        {
            "request": request,
        },
    )


@general_pages_router.get("/success/{file_name}", response_class=HTMLResponse)
async def general_transition_page_request(request: Request, file_name: str):
    file_path = Path(
        Path(__file__).parents[2],
        "templates",
        "general_pages",
        "pack_transition_pages",
        f"{file_name}.html",
    )
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Page not found")

    user_is_logged_in = await async_get_current_users_email() is not None
    config = await get_config_obj()
    return templates.TemplateResponse(
        str(Path("general_pages", "pack_transition_pages", f"{file_name}.html")),
        {
            "request": request,
            "user_is_logged_in": user_is_logged_in,
            "SUPA_URL": config.SUPA_STORAGE_URL,
            "PUB_KEY": config.SUPA_PUBLIC_KEY,
        },
    )


@general_pages_router.get("/{file_name}", response_class=HTMLResponse)
async def general_pages_route(request: Request, file_name: str):
    user_is_logged_in = await async_get_current_users_email() is not None
    config = await get_config_obj()
    file_path = Path(Path(__file__).parents[2], "templates", "general_pages", f"{file_name}.html")
    if not file_path.exists():
        return templates.TemplateResponse(
            str(Path("general_pages", "homepage.html")),
            {
                "request": request,
                "user_is_logged_in": user_is_logged_in,
            },
        )
    return templates.TemplateResponse(
        str(Path("general_pages", f"{file_name}.html")),
        {
            "request": request,
            "user_is_logged_in": user_is_logged_in,
            "SUPA_URL": config.SUPA_STORAGE_URL,
            "PUB_KEY": config.SUPA_PUBLIC_KEY,
        },
    )
