#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May  5 22:09:26 2023

@author: dale
"""

from sqlalchemy.orm import Session
from schemas.subscribers import SubscriberCreate
from db.models.subscribers import Subscriber
import datetime


def date_handler(obj):
    if isinstance(obj, datetime.date):
        return obj.isoformat()
    else:
        raise TypeError("Type %s not serializable" % type(obj))

def create_new_subscriber(
        subscriber:SubscriberCreate,
        db:Session):
    subscriber = Subscriber(
        email = str(subscriber.email),
        name = str(subscriber.name),
        zip_code = str(subscriber.zip_code),
        phone = str(subscriber.phone),
        agree_tos=True,
        date_posted=date_handler(datetime.datetime.now())
    )
    print(dir(db))
    db.add(subscriber)
    db.commit()
    db.refresh(subscriber)
    return subscriber


def remove_subscriber(
        subscriber_email: str,
        db:Session):
    subscriber = db.query(
        Subscriber
    ).filter(Subscriber.email == subscriber_email).first()

    if subscriber:
        db.delete(subscriber)
        db.commit()
        return {"email": subscriber_email}