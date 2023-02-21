from fastapi import FastAPI, Depends, Request
from fastapi.responses import RedirectResponse, HTMLResponse, JSONResponse
from app.models import LoginDetails, TranslateStatus, TranslateRequest, TranslateResponse
from app.auth.auth_handler import authenticate_user
from app.auth.auth_bearer import JWTBearer, signJWT
from app.mt_models.connection import MTRequestHandler
from fastapi.templating import Jinja2Templates

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

templates = Jinja2Templates(directory="app/templates")
mt_request_handler = MTRequestHandler()

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
    source = request.src
    target = request.tgt
    text = request.text

    translation = await mt_request_handler.translate(source, target, text)

    return JSONResponse(translation)

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

@app.get("/status", response_class=HTMLResponse, tags=["Maintenance"])
async def status(request: Request):
    global model_connections
    model_connections.connect_to_all()
    return templates.TemplateResponse("model_status.html", {"request": request, "connections": model_connections.all_as_dict()})

    
