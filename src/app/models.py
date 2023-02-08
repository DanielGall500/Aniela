from pydantic import BaseModel

class LoginDetails(BaseModel):
    username: str
    password: str

class TranslateRequest(BaseModel):
    src: str
    tgt: str
    text: str

class TranslateStatus:
    token_validated: bool = False
    translated: bool = False
    message: str = "Nothing to report."

class TranslateResponse:
    username: str
    status: TranslateStatus
