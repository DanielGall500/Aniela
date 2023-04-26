from locust import HttpUser, task, between
from dotenv import dotenv_values
from enum import Enum
import requests
import time
import json

class Language(Enum):
    English = 'en'
    German = 'de'
    Polish = 'pl'
    French = 'fr'
    Irish = 'ga'
    Italian = 'it'
    All = 'all'

#Choose the language to use
sample_sentences = {
    Language.English: "This is the daily test of the EUComMeet MT models.",
    Language.Italian: "Questo è il test quotidiano dei modelli EUComMeet MT.",
    Language.German: "Das ist der tägliche Test der EUComMeet MT-Modelle.",
    Language.French: "Il s'agit du test quotidien des modèles EUComMeet MT.",
    Language.Polish: "To jest codzienny test modeli EUComMeet MT.",
    Language.Irish: "Seo tástáil laethúil na samhlacha EUComMeet MT.",
}

# environment variables
env_config = dotenv_values()
username = env_config["USERNAME"]
password_v1 = env_config["PASSWORD_V1"]
password_v2 = env_config["PASSWORD_V2"]

# which version of the platform are we testing
IS_VERSION_TWO = True

#URL variables
domain = "https://mt.computing.dcu.ie"
trans_endpoint = '/translate'
login_endpoint = '/login'

#Login variables
username = "daniel"
password = password_v2 if IS_VERSION_TWO else password_v1
target_lang = Language.All

def get_token():
    # send all info necessary to receive a JWT
    resp = requests.post(
        url=domain + login_endpoint,
        data=json.dumps({
            "username": username,
            "password": password
        }),
        headers={
            'Content-Type': 'application/json'
        },
    )
    # get our JWT
    token = resp.json()['token']
    return token

token = get_token()

class QuickstartUser(HttpUser):
    wait_time = between(1, 2)

    def on_start(self):
        self.client.headers['Content-Type'] = 'application/json'
        # set headers for all further requests
        if IS_VERSION_TWO:
            self.client.headers['Authorization'] = 'Bearer ' + token
        else:
            self.client.headers['x-access-token'] = token

    @task
    def translate_from_german(self):
        self.translate_from(Language.German)

    @task
    def translate_from_english(self):
        self.translate_from(Language.English)

    @task
    def translate_from_italian(self):
        self.translate_from(Language.Italian)

    @task
    def translate_from_french(self):
        self.translate_from(Language.French)

    @task
    def translate_from_polish(self):
        self.translate_from(Language.Polish)

    @task
    def translate_from_irish(self):
        self.translate_from(Language.Irish)

    def translate_from(self, src: Language):
        # load the translation request data
        data = {
            "src": src.value,
            "tgt": "all",
            "text": sample_sentences[src]
        }

        # send the translation request
        resp = self.client.post(
            url=trans_endpoint,
            data=json.dumps(data),
            name=f"Translation: {src.name} => All",
        )

        # output the response
        print(resp.json())
