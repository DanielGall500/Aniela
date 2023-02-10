from fastapi import FastAPI, Depends
from fastapi.responses import RedirectResponse
from app.models import LoginDetails, TranslateStatus, TranslateRequest, TranslateResponse
from app.auth.auth_handler import authenticate_user
from app.auth.auth_bearer import JWTBearer, signJWT

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
        }
    ]
)

@app.get("/", tags=["Maintenance"])
async def root():
    return RedirectResponse(url="/redoc")

@app.get("/restart", tags=["Maintenance"])
async def restart():
    print("Restarting the server...")
    pass

@app.post("/translate", dependencies=[Depends(JWTBearer())], response_model=TranslateResponse, tags=["Translation Calls"])
async def translate(request: TranslateRequest):
    response = TranslateResponse()
    response.username = "Daniel"
    response.status = TranslateStatus()
    return response

@app.post("/login", tags=["User Authentication"])
async def login(request: LoginDetails):
    username = request.username
    password_attempt = request.password

    user_authentication = authenticate_user(username, password_attempt)
    if user_authentication["validated"]:
        token = signJWT(username)
        return { "access_token": token }
    else:
        return user_authentication
