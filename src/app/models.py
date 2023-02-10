from pydantic import BaseModel, Field

class LoginDetails(BaseModel):
    username: str
    password: str

class TranslateRequest(BaseModel):
    src: str = Field(description="The source language.")
    tgt: str = Field(description="The target language.")
    text: str = Field(description="The text which you want to translate.")

class TranslateStatus(BaseModel):
    token_validated: bool = False
    translated: bool = False
    message: str = "Nothing to report."

class TranslateResponse(BaseModel):
    username: str = Field("Unknown")
    status: TranslateStatus = Field(None)
