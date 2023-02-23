from starlette.testclient import TestClient
from app.api import app
import requests
from dotenv import dotenv_values
from app.mt_models.information import model_info

client = TestClient(app)

def test_default():
    response = client.get('/')
    assert response.status_code == 200

def test_login():
    parameters = {
        "username": "invalid",
        "password": "invalid"
    }
    headers = {"Content-Type": "application/json; charset=utf-8"}
    response = requests.post(url=model_info.get_server_url(), json=parameters, headers=headers)
    assert response.status_code == 500

def test_translate():
    response = client.post('/translate')
    assert response.status_code == 403