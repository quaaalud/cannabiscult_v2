#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May  5 22:15:24 2023

@author: dale
"""

from fastapi import APIRouter
from sqlalchemy.orm import Session
from fastapi import Depends

from db.session import get_supa_db
from schemas.subscribers import SubscriberCreate, ShowSubscriber
from db.repository.subscribers import create_new_subscriber
from db.models.subscribers import Subscriber

router = APIRouter()


@router.post("/", response_model=ShowSubscriber)
def create_subscriber(
    subscriber: SubscriberCreate,
    db: Session = Depends(get_supa_db)
):
    subscriber = create_new_subscriber(
        subscriber=subscriber,
        db=db
    )
    return subscriber


def remove_subscriber(subscriber_email: str,
                      db: Session = Depends(get_supa_db)
                      ):
    subscriber = db.query(
        Subscriber
    ).filter(Subscriber.email == subscriber_email).first()

    if subscriber:
        db.delete(subscriber)
        db.commit()
        return {"email": subscriber_email}
