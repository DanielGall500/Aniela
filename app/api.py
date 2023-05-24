from fastapi import FastAPI, Depends, Request, status, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, HTMLResponse
from app.models import LoginDetails, TranslateRequest, TranslateResponse, DeleteRequest
from app.auth.auth_handler import authenticate_user
from app.auth.auth_bearer import JWTBearer, signJWT
from app.mt_models.connection import MTRequestHandler
from app.mt_models.connection import MTServerConnection
from app.mt_models.information import model_info
from fastapi.templating import Jinja2Templates
from loguru import logger
from datetime import datetime
from typing import Annotated
import sqlite3
import time

app = FastAPI(
    title="Adapt Translation API",
    description="This API provides efficient and secure connection to 30 language models comprising of six available language: English, German, French, Italian, Polish, and Irish.",
    version="2.0",
    contact={
        "name": "Adapt Centre, Dublin City University",
        "url": "https://www.adaptcentre.ie/",
    },
    openapi_tags=[
        {
            "name": "Translation Calls",
            "description": "Any routes for calling the translation services. Each language has a specific code associated with it which should be used when passing the JSON parameters. English is 'en', German is 'de', French is 'fr', Italian is 'it', Polish is 'pl', and Irish is 'ga'. In order to make translations, you first need to ensure that you are logged in. Please see the authentication routes for more information."
        },
        {
            "name": "User Authentication",
            "description": "Any routes which handle authentication of a user. A username and password must be provided in order to login which should have been provided to you by Adapt. Passwords should never be shared and are encrypted with Argon2 encryption for security."
        },
        {
            "name": "Maintenance & Testing",
            "description": "Any routes which can be used by users to find more information about the machine translation models and also test their current operational status."
        },
    ],
    redoc_url="/dashboard/docs",
    docs_url=None
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")
logger.add("logs/translate-api.log", rotation="1 day")

db_connection = sqlite3.connect("app/database.sqlite", check_same_thread=False)
cursor = db_connection.cursor()

mt_request_handler = MTRequestHandler()
mt_server_connection = MTServerConnection()

@app.post("/translate", dependencies=[Depends(JWTBearer())], response_model=TranslateResponse, 
    tags=["Translation Calls"], status_code=status.HTTP_201_CREATED,
    description="Submit a translation request to the API. A JSON web token must be provided in the header which is given to you once you log in.") 
def translate(request: TranslateRequest):
    # set up the translation
    source = request.src
    target = request.tgt
    text = request.text

    logger.info("Translation Request: {}-{}", source, target)
    logger.info("Text: {}", text)

    start_time = time.time()
    translation = mt_request_handler.translate(source, target, text)
    latency_time = round(time.time() - start_time, 4)

    # create the translation response
    response = TranslateResponse()
    response.username = "Unknown"
    response.status = translation["state"] 
    response.result = translation["result"]

    if response.status == mt_request_handler.STATUS_OK:
        logger.success("Result: {}", response.result)
        logger.success("Latency: {}", latency_time)

        store_translation(source, target, text, response.result, latency_time)

    else:
        logger.error("Translation unsuccessful.")

    return response

def store_translation(source, target, src_input, tgt_output, latency):
    store_translation_query = """INSERT INTO translations
                            (time, source, target, input, output, latency) 
                            VALUES 
                            (?, ?, ?, ?, ?, ?);"""
    try:
        cursor.execute(store_translation_query, (datetime.now(), str(source), str(target), str(src_input), str(tgt_output), float(latency)))
        db_connection.commit()
    except sqlite3.Error as error:
        logger.error("Failed to store translation data.")
        logger.error(error)


@app.post("/login", status_code=status.HTTP_201_CREATED, tags=["User Authentication"],
    description="Log in using your username and password in order to receive a JWT.")
async def login(request: LoginDetails):
    username = request.username
    password_attempt = request.password

    user_authentication = authenticate_user(username, password_attempt)
    if user_authentication["validated"]:
        token = signJWT(username)
        logger.success("{} logged in.", username)
        return { "token": token }
    else:
        logger.warning("Invalid login from {} with password {}", username, password_attempt)
        return user_authentication

# -- Translation API Dashboard Endpoints --
@app.get("/dashboard", response_class=HTMLResponse, 
    description="Check the status of each of the language models", tags=["Maintenance & Testing"])
async def dashboard(request: Request):
    logger.info("Dashboard accessed.")
    mt_server_connection.connect_to_all()
    as_dict = mt_server_connection.all_as_dict()
    return templates.TemplateResponse("index.html", {"request": request, "connections": as_dict})

@app.get("/", include_in_schema=False, tags=["Maintenance & Testing"])
async def root():
    return RedirectResponse(url="/dashboard")

@app.get("/dashboard/about", response_class=HTMLResponse, 
    description="Check the status of each of the language models", include_in_schema=False, tags=["Maintenance & Testing"])
async def about(request: Request):
    logger.info("About page accessed.")
    return templates.TemplateResponse("about.html", {"request": request})

@app.get("/dashboard/setup", response_class=HTMLResponse, 
    description="View and edit the current server setup for your models.", include_in_schema=False, tags=["Maintenance & Testing"])
async def setup(request: Request):
    logger.info("Setup page accessed.")
    model_info.refresh()
    server_config = model_info.get_config()
    return templates.TemplateResponse("setup.html", {"request": request, "server_config": server_config})

@app.post("/dashboard/setup/add")
async def add(
    request: Request,
    source: Annotated[str, Form()], 
    target: Annotated[str, Form()], 
    server: Annotated[str, Form()], 
    gpu: Annotated[str, Form()], 
    modelId: Annotated[str, Form()]
):
    add_model_query = """INSERT INTO models
                            (source, target, server, gpu, id) 
                        VALUES 
                            (?, ?, ?, ?, ?);"""
    try:
        cursor.execute(add_model_query, (source, target, server, gpu, modelId))
        db_connection.commit()
        logger.success("New model added to database.")
    except sqlite3.Error as error:
        logger.error("Failed to add new model.")
        logger.error(error)

    model_info.refresh()
    return RedirectResponse("/dashboard/setup", status_code=status.HTTP_303_SEE_OTHER) 

@app.post("/dashboard/setup/delete")
async def delete(
    request: DeleteRequest,
):
    model_id = request.model_id

    delete_model_query = """DELETE FROM models
                            WHERE id=?;"""
    try:
        cursor.execute(delete_model_query, (model_id,))
        db_connection.commit()
        logger.success("Model removed from setup.")
    except sqlite3.Error as error:
        logger.error("Failed to delete model from setup.")
        logger.error(error)

    return RedirectResponse("/dashboard/setup", status_code=status.HTTP_303_SEE_OTHER) 