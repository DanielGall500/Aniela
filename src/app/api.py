from fastapi import FastAPI, Depends
from fastapi.responses import RedirectResponse
from app.models import LoginDetails, TranslateStatus, TranslateRequest, TranslateResponse
from app.auth.auth_handler import authenticate_user
from app.auth.auth_bearer import JWTBearer, signJWT

app = FastAPI()

@app.get("/", tags=["Testing"])
async def root():
    return RedirectResponse(url="/docs")


@app.post("/translate", dependencies=[Depends(JWTBearer())], tags=["Translation Calls"])
async def translate(request: TranslateRequest):
    response = TranslateResponse()
    response.message = "Translations successful!"
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
