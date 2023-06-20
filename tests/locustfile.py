from locust import HttpUser, task, between
from dotenv import dotenv_values
from enum import Enum
import requests
import json

"""-EXAMPLE TEST WITH LOCUST----------------------------------------------------------------------
This is an example of a locustfile which can be used to test the performance of the API and your
machine translation models in real-time. It imitates N users, making translation requests with the
parameters set below. It is set up for 6 languages as an example.
-----------------------------------------------------------------------------------------------"""

class Language(Enum):
    English = 'en'
    German = 'de'
    Polish = 'pl'
    French = 'fr'
    Irish = 'ga'
    Italian = 'it'
    All = 'all'

sample_sentences = {
    Language.English: "This is the daily test of the EUComMeet MT models.",
    Language.Italian: "Questo è il test quotidiano dei modelli EUComMeet MT.",
    Language.German: "Das ist der tägliche Test der EUComMeet MT-Modelle.",
    Language.French: "Il s'agit du test quotidien des modèles EUComMeet MT.",
    Language.Polish: "To jest codzienny test modeli EUComMeet MT.",
    Language.Irish: "Seo tástáil laethúil na samhlacha EUComMeet MT.",
}

# import the example username and password
# from the environment variables file which
# you have set up.
env_config = dotenv_values()
username = env_config["TEST_USERNAME"]
password = env_config["TEST_PASSWORD"]

#URL variables
domain = "127.0.0.1"
trans_endpoint = '/translate'
login_endpoint = '/login'

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

    # set up our headers on starting the testing
    def on_start(self):
        self.client.headers['Content-Type'] = 'application/json'
        self.client.headers['Authorization'] = 'Bearer ' + token

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

    # send a translation request
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
