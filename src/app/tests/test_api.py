from starlette.testclient import TestClient
from dotenv import dotenv_values
from app.api import app
import requests
import json

# Environment variables used for testing
config_app: dict = dotenv_values('app/.env')
TEST_USERNAME: str = config_app["TEST_USERNAME"]
TEST_PASSWORD: str = config_app["TEST_PASSWORD"]
DEFAULT_HEADERS: dict = {"Content-Type": "application/json; charset=utf-8"}

# URL to which the tests should be sending requests
# This is the URL of the web server and not the MT servers
WEB_SERVER_IP: str = config_app["WEB_SERVER_IP"]
WEB_SERVER_PORT: str = config_app["WEB_SERVER_PORT"]
WEB_SERVER_URL: str = f"http://{WEB_SERVER_IP}:{WEB_SERVER_PORT}"
WEB_SERVER_LOGIN_URL: str = WEB_SERVER_URL + "/login"
WEB_SERVER_TRANSLATE_URL: str = WEB_SERVER_URL + "/translate"

client = TestClient(app)

# Tests of the most important API endpoints
def test_default():
    response = client.get('/')
    assert response.status_code == 200

def test_login():
    response = get_token(TEST_USERNAME, TEST_PASSWORD)
    assert "access_token" in response

def test_translate():
    # Set up the configuration for sending the request
    # This includes the parameters, headers, and translation URL
    parameters = {
        "src": "de",
        "tgt": "en",
        "text": "Klimawandel"
    }

    token = get_token(TEST_USERNAME, TEST_PASSWORD)["access_token"]
    translation_headers = set_token(DEFAULT_HEADERS, token)
    
    response = requests.post(url=WEB_SERVER_TRANSLATE_URL, json=parameters, headers=translation_headers)
    assert response.status_code == 200

# Token helper functions
def get_token(username: str, password: str):
    parameters = {
        "username": username,
        "password": password
    }
    response = requests.post(url=WEB_SERVER_LOGIN_URL, json=parameters, headers=DEFAULT_HEADERS)
    token = json.loads(response.content)
    return token

def set_token(headers: dict, token: str):
    headers['Authorization'] = 'Bearer ' + token
    return headers