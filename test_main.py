import os
from unittest.mock import patch
from fastapi.testclient import TestClient
from main import app 

client = TestClient(app)

@patch.dict(os.environ, {"USERNAME": "Mihai"})
def test_validate_quality_accept():
    response = client.post(
        "/validate-quality", 
        json={
            "identifier_name": "88823141",
            "master_name": "CM-10001",
            "characteristic_name": "Volume",
            "measured_value": 505.0
        }, 
        headers={"x-username": "Mihai"}
    )
    assert response.status_code == 200
    assert response.json()["decizie"] == "ACCEPTAT"

@patch.dict(os.environ, {"USERNAME": "Mihai"})
def test_validate_quality_reject():
    response = client.post(
        "/validate-quality", 
        json={
            "identifier_name": "88823141",
            "master_name": "CM-10001",
            "characteristic_name": "Volume",
            "measured_value": 100.0
        }, 
        headers={"x-username": "Mihai"}
    )
    assert response.status_code == 200
    assert response.json()["decizie"] == "RESPINS"

@patch.dict(os.environ, {"USERNAME": "Mihai"})
def test_validate_quality_unauthorized():
    response = client.post(
        "/validate-quality", 
        json={
            "identifier_name": "88823141",
            "master_name": "CM-10001",
            "characteristic_name": "Volume",
            "measured_value": 505.0
        }, 
        headers={"x-username": "Hacker_User"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Unauthorized"