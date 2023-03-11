#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 11 10:18:28 2023

@author: dale
"""

import json


def test_create_user(client):
    data = {
        "username":"testuser",
        "email":"testuser@nofoobar.com",
        "password":"testing",
    }
    response = client.post("/users/",json.dumps(data))
    assert response.status_code == 200 
    assert response.json()["email"] == "testuser@nofoobar.com"
    assert response.json()["is_active"] == True