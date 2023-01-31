from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import RedirectResponse
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
import sqlite3
import jwt

class TranslateItem(BaseModel):
    src: str
    tgt: str
    text: str

class LoginDetails(BaseModel):
    username: str
    password: str

app = FastAPI()
auth_db = sqlite3.connect("authentication.sqlite")
cursor = auth_db.cursor()
ph = PasswordHasher()

@app.get("/")
async def root():
    return RedirectResponse(url="/docs")

@app.post("/translate")
async def translate(request: TranslateItem):
    return request

@app.post("/login")
async def login(request: LoginDetails):
    username = request.username
    pass_attempt = request.password
    try:
        password_query = get_password_query(username)
        if(password_query["exists"]):
            hash = password_query["hash"]
            is_valid_login = ph.verify(hash, pass_attempt)
            return {"status": is_valid_login}
        else:
            return {"status": "User not found."}
    except VerifyMismatchError:
        return {"status": "Invalid credentials."}

def get_password_query(username):
    pass_query = cursor.execute(f"SELECT password FROM users WHERE username='{username}';").fetchone()
    pass_exists = pass_query != None
    if(pass_exists):
        pass_hash = pass_query[0]
        return {"exists": pass_exists, "hash": pass_hash}
    else:
        return {"exists": pass_exists}
    
