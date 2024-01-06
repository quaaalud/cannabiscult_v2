#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar  5 21:10:59 2023
@author: dale
"""


from pathlib import Path
from fastapi import APIRouter, Request, Form, Depends, Query, HTTPException

# from fastapi import BackgroundTasks
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from gotrue.errors import AuthApiError
from typing import List, Optional, Dict, Any
from db.session import get_db
from core.config import settings, Config
from db.repository.edibles import get_vivd_edible_data_by_strain
from db.repository.edibles import get_vibe_edible_data_by_strain
from route_subscribers import create_subscriber, remove_subscriber
from route_users import (
    create_user,
    create_supa_user,
    login_supa_user,
    get_current_users_email,
    async_get_current_users_email,
    return_current_user_vote_status,
    update_user_password,
    logout_current_user,
)
from schemas.mystery_voters import MysteryVoterCreate
from schemas.subscribers import SubscriberCreate
from schemas.users import UserCreate, ShowUser, UserLogin, LoggedInUser
from version1._supabase.route_flower_reviews import (
    get_all_strains,
    get_all_cultivators,
    get_all_strains_for_cultivator,
    get_all_cultivators_for_strain,
    return_selected_review,
    add_new_votes_to_flower_strain,
)
from version1._supabase.route_flower_voting import (
    add_flower_vote_to_db,
)
from db.repository.flowers import get_flower_and_description
from version1._supabase import route_concentrates
from db.repository import concentrate_reviews
from db.repository.concentrates import get_concentrate_data_and_path
from version1._supabase.route_mystery_voters import get_voter_info_by_email, create_mystery_voter

templates_dir = Path(
    Path(__file__).parents[2],
    "templates",
)

templates = Jinja2Templates(directory=str(templates_dir))
general_pages_router = APIRouter()


@general_pages_router.get("/")
async def home(request: Request):
    partner_data = await get_current_partner_data()
    user_is_logged_in = await async_get_current_users_email() is not None
    return templates.TemplateResponse(
        str(Path("general_pages", "homepage.html")),
        {
            "request": request,
            "dispensaries": partner_data,
            "user_is_logged_in": user_is_logged_in,
        },
    )


@general_pages_router.get("/voting-home")
async def voting_home(request: Request):
    user_is_logged_in = await async_get_current_users_email() is not None
    return templates.TemplateResponse(
        str(Path("general_pages", "voting-home.html")),
        {
            "request": request,
            "user_is_logged_in": user_is_logged_in,
        },
    )


@general_pages_router.post("/login-submit", response_model=LoggedInUser)
async def submit_login_form(
    request: Request,
    login_email: str = Form(...),
    login_password: str = Form(...),
) -> templates.TemplateResponse:

    user = UserLogin(
        email=login_email.lower(),
        password=login_password,
    )
    try:
        user = login_supa_user(user=user)
        return templates.TemplateResponse(
            str(Path("general_pages", "login_success.html")),
            {
                "request": request,
                "username": login_email.lower(),
                "user": user,
            },
        )
    except AuthApiError:
        return templates.TemplateResponse(
            str(Path("general_pages", "submit-failed.html")),
            {
                "request": request,
                "username": login_email.lower(),
            },
        )


@general_pages_router.post("/register", response_model=ShowUser)
async def submit_register_form(
    request: Request,
    register_email: str = Form(...),
    register_password: str = Form(...),
    register_repeat_password: str = Form(...),
    register_name: str = Form(...),
    register_username: str = Form(...),
    register_zip_code: str = Form(...),
    register_phone: str = Form(...),
    db: Session = Depends(get_db),
) -> templates.TemplateResponse:
    if register_password == register_repeat_password:
        user = UserCreate(
            email=str(register_email.lower()),
            password=register_password,
            name=register_name,
            username=register_username,
            phone=register_phone,
            zip_code=register_zip_code,
            agree_tos=True,
            can_vote=False,
            is_superuser=False,
        )

        create_user(user=user, db=db)
        create_supa_user(user=user)

        existing_voter = get_voter_info_by_email(register_email.lower(), db)
        if not existing_voter:
            try:
                voter = MysteryVoterCreate(
                    email=register_email.lower(),
                    name=register_name,
                    zip_code=register_zip_code,
                    phone=register_phone,
                )
                create_mystery_voter(voter=voter, db=db)
            except Exception as e:
                print(f"Error: {e}\n\n{e.with_traceback()}")
                pass

        return templates.TemplateResponse(
            str(Path("general_pages", "register_success.html")),
            {
                "request": request,
                "username": register_name,
            },
        )
    else:
        return templates.TemplateResponse(
            str(Path("general_pages", "submit-failed.html")),
            {
                "request": request,
                "username": register_name,
            },
        )


@general_pages_router.post("/logout-submit", response_model=None)
async def submit_user_logout(
    request: Request, db: Session = Depends(get_db)
) -> templates.TemplateResponse:
    user = get_current_users_email()
    try:
        if user:
            logout_current_user()
    except AuthApiError:
        pass
    finally:
        partner_data = await get_current_partner_data()
        return templates.TemplateResponse(
            str(Path("general_pages", "logout_success.html")),
            {
                "request": request,
                "dispensaries": partner_data,
                "user_is_logged_in": user is not None,
            },
        )


@general_pages_router.post("/submit-new-password", response_model=ShowUser)
async def submit_new_password_form(
    request: Request,
    user_email: str = Form(...),
    username: str = Form(...),
    new_password: str = Form(...),
    repeated_password: str = Form(...),
    db: Session = Depends(get_db),
) -> templates.TemplateResponse:

    user_is_logged_in = get_current_users_email() is not None

    try:
        user = update_user_password(
            user_email=user_email.lower(),
            username=username,
            new_password=new_password,
            repeated_password=repeated_password,
            db=db,
        )
        return templates.TemplateResponse(
            str(Path("general_pages", "register_success.html")),
            {
                "request": request,
                "username": user_email.lower(),
                "can_vote_status": user.can_vote,
            },
        )
    except:
        return templates.TemplateResponse(
            str(Path("general_pages", "submit-failed.html")),
            {
                "request": request,
                "user_is_logged_in": user_is_logged_in,
            },
        )


@general_pages_router.post("/submit", response_model=None)
async def submit_subscriber_form(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    zip_code: str = Form(...),
    db: Session = Depends(get_db),
) -> templates.TemplateResponse:

    subscriber_data = SubscriberCreate(
        email=email.lower(),
        name=name,
        zip_code=zip_code,
        phone=phone,
    )
    create_subscriber(subscriber=subscriber_data, db=db)

    return templates.TemplateResponse(
        str(Path("general_pages", "success.html")),
        {
            "request": request,
            "name": name,
            "email": email.lower(),
            "phone": phone,
            "zip_code": zip_code,
        },
    )


@general_pages_router.get("/privacy-policy")
async def privacy_policy(request: Request):
    user_is_logged_in = get_current_users_email() is not None
    return templates.TemplateResponse(
        str(Path("general_pages", "privacy_policy.html")),
        {
            "request": request,
            "user_is_logged_in": user_is_logged_in,
        },
    )


@general_pages_router.get("/terms-of-use")
async def terms_and_conditions(request: Request):
    user_is_logged_in = get_current_users_email() is not None
    return templates.TemplateResponse(
        str(Path("general_pages", "terms_and_conditions.html")),
        {
            "request": request,
            "user_is_logged_in": user_is_logged_in,
        },
    )


@general_pages_router.post("/unsubscribe-submit", response_model=None)
async def submit_unsubscribe_form(
    request: Request, email: str = Form(...), db: Session = Depends(get_db)
) -> templates.TemplateResponse:

    remove_subscriber(email, db=db)

    partner_data = await get_current_partner_data()
    return templates.TemplateResponse(
        str(Path("general_pages", "homepage.html")),
        {
            "request": request,
            "dispensaries": partner_data,
        },
    )


@general_pages_router.get("/get-all-strains", response_model=List[str])
async def get_all_strains_route(db: Session = Depends(get_db)) -> List[str]:
    return get_all_strains(db)


@general_pages_router.get("/get-all-cultivators", response_model=List[str])
async def get_all_cultivators_route(db: Session = Depends(get_db)) -> List[str]:
    return get_all_cultivators(db)


@general_pages_router.get("/get-strains-for-cultivator", response_model=List[str])
async def get_all_strains_for_cultivator_route(
    cultivator_selected: str = Query(...), db: Session = Depends(get_db)
) -> List[str]:
    return get_all_strains_for_cultivator(cultivator_selected, db)


@general_pages_router.get("/get-cultivators-for-strain", response_model=List[str])
async def get_all_cultivators_for_strain_route(
    strain_selected: str = Query(...), db: Session = Depends(get_db)
) -> List[str]:
    return get_all_cultivators_for_strain(strain_selected, db)


async def process_flower_request(
    request: Request, strain_selected: str, cultivator_selected: str, db: Session
):
    user_is_logged_in = get_current_users_email() is not None
    review_dict = await get_flower_and_description(
        db=db, strain=strain_selected, cultivator=cultivator_selected
    )
    try:
        request_dict = {
            "request": request,
            "user_is_logged_in": user_is_logged_in,
        }
        response_dict = {**request_dict, **review_dict}
        return templates.TemplateResponse(
            str(Path("general_pages", "connoisseur_flowers.html")), response_dict
        )
    except:
        return templates.TemplateResponse(
            str(Path("general_pages", "voting-home.html")),
            {
                "request": request,
            },
        )


@general_pages_router.post("/get-review", response_model=Dict[str, Any])
async def handle_flower_review_get(
    request: Request,
    *,
    strain_selected: str = Form(None),
    cultivator_selected: str = Form(None),
    product_type_selected_selected: str = Form("flower"),
    db: Session = Depends(get_db),
):
    return await process_flower_request(request, strain_selected, cultivator_selected, db)


@general_pages_router.get("/get-review")
async def handle_flower_review_post(
    request: Request,
    *,
    strain_selected: str = Query(None, alias="strain_selected"),
    cultivator_selected: str = Query(None, alias="cultivator_selected"),
    product_type_selected: str = Query("flower", alias="product_type_selected"),
    db: Session = Depends(get_db),
):
    return await process_flower_request(request, strain_selected, cultivator_selected, db)


@general_pages_router.get("/get_hidden_concentrate")
async def handle_hidden_concentrate_post(
    request: Request, strain: str = Query(None, alias="strain"), db: Session = Depends(get_db)
):
    hidden_concentrate_dict = get_concentrate_data_and_path(
        db,
        strain=strain,
    )
    response_dict = {"request": request, **hidden_concentrate_dict}
    return templates.TemplateResponse(
        str(Path("general_pages", "connoisseur_concentrates.html")), response_dict
    )


@general_pages_router.get("/get-vivid-edible")
async def handle_vivid_edible_post(
    request: Request,
    edible_strain: str = Query(None, alias="edible_strain"),
    db: Session = Depends(get_db),
):
    edible_dict = get_vivd_edible_data_by_strain(
        db,
        edible_strain=edible_strain,
    )
    response_dict = {"request": request, **edible_dict}
    return templates.TemplateResponse(
        str(Path("general_pages", "vivid-edible-ratings.html")), response_dict
    )


@general_pages_router.get("/get-vibe-edible")
@general_pages_router.get("/edible-get-review")
async def handle_vibe_edible_post(
    request: Request,
    edible_strain: str = Query(None, alias="edible_strain"),
    product_type_selected: str = Query(None, alias="product_type_selected"),
    cultivator_selected: str = Query(None, alias="cultivator_selected"),
    strain_selected: str = Query(None, alias="strain_selected"),
    db: Session = Depends(get_db),
):
    # Decide which strain to use based on the provided parameters
    strain_to_use = strain_selected if strain_selected else edible_strain

    # Additional logic to handle product_type_selected and cultivator_selected if needed

    edible_dict = get_vibe_edible_data_by_strain(
        db,
        edible_strain=strain_to_use,
    )
    response_dict = {"request": request, **edible_dict}
    return templates.TemplateResponse(
        str(Path("general_pages", "vibe-edible-ratings.html")), response_dict
    )


@general_pages_router.get("/vibe_concentrate_ratings")
async def vibe_concentrates_main_page(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse(
        str(Path("general_pages", "vibe-concentrate-ratings.html")), {"request": request}
    )


@general_pages_router.get("/get_vibe_concentrate")
async def handle_vibe_concentrate_post(
    request: Request, strain: str = Query(None, alias="strain"), db: Session = Depends(get_db)
):
    concentrate_dict = get_concentrate_data_and_path(
        db,
        strain=strain,
    )
    response_dict = {"request": request, **concentrate_dict}
    return templates.TemplateResponse(
        str(Path("general_pages", "vibe-concentrate-ratings.html")), response_dict
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
    structure_explanation: str = Form("None"),
    nose_explanation: str = Form("None"),
    flavor_explanation: str = Form("None"),
    effects_explanation: str = Form("None"),
    db: Session = Depends(get_db),
    current_user_email=Depends(get_current_users_email),
) -> templates.TemplateResponse:

    can_vote_status = return_current_user_vote_status(
        user_email=current_user_email,
        db=db,
    )

    user_email = get_current_users_email()
    user_is_logged_in = user_email is not None

    if not can_vote_status:
        return templates.TemplateResponse(
            str(Path("general_pages", "login.html")),
            {
                "request": request,
                "user_is_logged_in": user_is_logged_in,
            },
        )
    try:
        add_flower_vote_to_db(
            cultivator_selected=cultivator_selected,
            strain_selected=strain_selected,
            structure_vote=structure_vote,
            structure_explanation=structure_explanation,
            nose_vote=nose_vote,
            nose_explanation=nose_explanation,
            flavor_vote=flavor_vote,
            flavor_explanation=flavor_explanation,
            effects_vote=effects_vote,
            effects_explanation=effects_explanation,
            user_email=user_email,
            db=db,
        )
    except:
        pass
    try:
        review_dict = add_new_votes_to_flower_strain(
            cultivator_selected,
            strain_selected,
            structure_vote,
            nose_vote,
            flavor_vote,
            effects_vote,
            db,
        )

        request_dict = {
            "request": request,
            "user_is_logged_in": user_is_logged_in,
        }
        response_dict = {**request_dict, **review_dict}
        return templates.TemplateResponse(
            str(Path("general_pages", "vote_success.html")), response_dict
        )
    except:
        return templates.TemplateResponse(
            str(Path("general_pages", "voting-home.html")),
            {
                "request": request,
                "user_is_logged_in": user_is_logged_in,
            },
        )


@general_pages_router.get("/concentrate-get-all-strains", response_model=List[str])
async def get_concentrate_strains_route(db: Session = Depends(get_db)) -> List[str]:
    return route_concentrates.get_all_strains(db)


@general_pages_router.get("/concentrate-get-all-cultivators", response_model=List[str])
async def get_concentrate_cultivators_route(db: Session = Depends(get_db)) -> List[str]:
    return route_concentrates.get_all_cultivators(db)


@general_pages_router.get("/concentrate-get-strains-for-cultivator", response_model=List[str])
async def get_concentrate_strains_for_cultivator_route(
    cultivator_selected: str = Query(...), db: Session = Depends(get_db)
) -> List[str]:
    return route_concentrates.get_all_strains_for_cultivator(cultivator_selected, db)


@general_pages_router.get("/concentrate-get-cultivators-for-strain", response_model=List[str])
async def get_concentrate_cultivators_for_strain_route(
    strain_selected: str = Query(...), db: Session = Depends(get_db)
) -> List[str]:
    return route_concentrates.get_all_cultivators_for_strain(strain_selected, db)


async def process_concentrate_request(
    request: Request, strain_selected: str, cultivator_selected: str, db: Session
):
    review_dict = await route_concentrates.get_concentrate_by_strain_and_cultivator(
        strain=strain_selected, cultivator=cultivator_selected, db=db
    )
    if review_dict:
        request_dict = {
            "request": request,
        }
        response_dict = {**request_dict, **review_dict}
        if response_dict.get("is_mystery") is True:
            return templates.TemplateResponse(
                str(Path("general_pages", "connoisseur_concentrates.html")), response_dict
            )
        else:
            review_dict = await route_concentrates.get_concentrate_and_description(
                db=db,
                strain=strain_selected,
                cultivar_email="aaron.childs@thesocialoutfitus.com",
                cultivator=cultivator_selected,
            )
            request_dict = {
                "request": request,
            }
            response_dict = {**request_dict, **review_dict}
            return templates.TemplateResponse(
                str(Path("general_pages", "concentrate_ratings.html")), response_dict
            )
    try:
        review_dict = concentrate_reviews.get_review_data_and_path(
            cultivator_select=cultivator_selected, strain_select=strain_selected, db=db
        )
        request_dict = {
            "request": request,
        }
        response_dict = {**request_dict, **review_dict}

        return templates.TemplateResponse(
            str(Path("general_pages", "concentrate_ratings.html")), response_dict
        )
    except:
        return templates.TemplateResponse(
            str(Path("general_pages", "voting-home.html")),
            {
                "request": request,
            },
        )


@general_pages_router.post("/concentrate-get-review")
async def handle_concentrate_review_get(
    request: Request,
    *,
    strain_selected: str = Form(None),
    cultivator_selected: str = Form(None),
    product_type_selected: str = Form("concentrate"),
    db: Session = Depends(get_db),
):
    return await process_concentrate_request(request, strain_selected, cultivator_selected, db)


@general_pages_router.get("/concentrate-get-review")
async def handle_concentrate_review_post(
    request: Request,
    *,
    strain_selected: str = Query(None, alias="strain_selected"),
    cultivator_selected: str = Query(None, alias="cultivator_selected"),
    product_type_selected: str = Query("concentrate", alias="product_type_selected"),
    db: Session = Depends(get_db),
):
    return await process_concentrate_request(request, strain_selected, cultivator_selected, db)


@general_pages_router.post("/concentrate-submit-vote", response_model=List[str])
async def submit_concentrate_review_vote(
    request: Request,
    strain_selected: str = Form(...),
    cultivator_selected: str = Form(...),
    structure_vote: str = Form(...),
    nose_vote: str = Form(...),
    flavor_vote: str = Form(...),
    effects_vote: str = Form(...),
    structure_explanation: str = Form("None"),
    nose_explanation: str = Form("None"),
    flavor_explanation: str = Form("None"),
    effects_explanation: str = Form("None"),
    db: Session = Depends(get_db),
    current_user_email=Depends(get_current_users_email),
) -> templates.TemplateResponse:

    can_vote_status = return_current_user_vote_status(
        user_email=current_user_email.lower(),
        db=db,
    )

    user_email = get_current_users_email()
    user_is_logged_in = user_email is not None

    if not can_vote_status:
        return templates.TemplateResponse(
            str(Path("general_pages", "login.html")),
            {
                "request": request,
                "user_is_logged_in": user_is_logged_in,
            },
        )
    try:
        route_concentrates.add_concentrate_vote_to_db(
            cultivator_selected=cultivator_selected,
            strain_selected=strain_selected,
            structure_vote=structure_vote,
            structure_explanation=structure_explanation,
            nose_vote=nose_vote,
            nose_explanation=nose_explanation,
            flavor_vote=flavor_vote,
            flavor_explanation=flavor_explanation,
            effects_vote=effects_vote,
            effects_explanation=effects_explanation,
            user_email=user_email.lower(),
            db=db,
        )
    except:
        pass
    try:
        review_dict = route_concentrates.add_new_votes_to_concentrate_values(
            cultivator_selected,
            strain_selected,
            structure_vote,
            nose_vote,
            flavor_vote,
            effects_vote,
            db,
        )

        request_dict = {
            "request": request,
            "user_is_logged_in": user_is_logged_in,
        }
        response_dict = {**request_dict, **review_dict}
        return templates.TemplateResponse(
            str(Path("general_pages", "vote_success.html")), response_dict
        )
    except:
        return templates.TemplateResponse(
            str(Path("general_pages", "voting-home.html")),
            {
                "request": request,
                "user_is_logged_in": user_is_logged_in,
            },
        )


@general_pages_router.get("/check-mystery-voter", response_model=Optional[Dict[str, bool]])
def check_mystery_voter_email_by_get(
    voter_email: str = Query(None, alias="voter_email"), db: Session = Depends(get_db)
) -> Optional[Dict[str, bool]]:
    voter = get_voter_info_by_email(voter_email=voter_email.lower(), db=db)
    if not voter:
        return {"exists": False}
    return {"exists": True}


@general_pages_router.get("/check-mystery-voter", response_model=Optional[Dict[str, bool]])
def check_mystery_voter_email(
    voter_email: str = Form(...), db: Session = Depends(get_db)
) -> Optional[Dict[str, bool]]:
    voter = get_voter_info_by_email(voter_email=voter_email.lower(), db=db)
    if not voter:
        return {"exists": False}
    return {"exists": True}


@general_pages_router.post("/submit-new-voter", response_model=None)
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
    except:
        return {"status": False}


@general_pages_router.get("/config")
async def get_config():
    return Config(
        SUPA_STORAGE_URL=settings.SUPA_STORAGE_URL,
        SUPA_PUBLIC_KEY=settings.SUPA_PUBLIC_KEY,
        ALGO=settings.ALGO,
    )


async def get_config_obj():
    return Config(
        SUPA_STORAGE_URL=settings.SUPA_STORAGE_URL,
        SUPA_PUBLIC_KEY=settings.SUPA_PUBLIC_KEY,
        ALGO=settings.ALGO,
    )


@general_pages_router.get("/{subdomain}.cannabiscult.co")
async def redirect_to_auth_provider(subdomain: str, auth_url: str = None):
    if not auth_url:
        raise HTTPException(status_code=400, detail="auth_provider_url must be provided")
    return RedirectResponse(url=auth_url)


async def get_current_partner_data():
    import get_partner_gsheet.get_gsheet_pandas as get_gsheet

    return get_gsheet._get_deal_workbook_and_return_dict()


@general_pages_router.get("/sitemap.xml")
async def sitemap(request: Request):
    return templates.TemplateResponse(
        str(Path("general_pages", "sitemap.xml")),
        {
            "request": request,
        },
    )


@general_pages_router.get("/{file_name}")
async def general_pages_route(request: Request, file_name: str):
    file_path = Path(Path(__file__).parents[2], "templates", "general_pages", f"{file_name}.html")
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Page not found")

    partner_data = await get_current_partner_data()
    user_is_logged_in = await async_get_current_users_email() is not None
    config = await get_config_obj()
    return templates.TemplateResponse(
        str(Path("general_pages", f"{file_name}.html")),
        {
            "request": request,
            "dispensaries": partner_data,
            "user_is_logged_in": user_is_logged_in,
            "SUPA_URL": config.SUPA_STORAGE_URL,
            "PUB_KEY": config.SUPA_PUBLIC_KEY,
        },
    )
