from pydantic import BaseModel, Field

class LoginDetails(BaseModel):
    username: str
    password: str

class TranslateRequest(BaseModel):
    src: str = Field(description="The source language.")
    tgt: str = Field(description="The target language.")
    text: str = Field(description="The text which you want to translate.")

class TranslateResponse(BaseModel):
    username: str = Field("John Doe", description="The user who sent the original request.")
    status: str = Field("SUCCESS", description="The return status of the request - either SUCCESS or ERROR.")
    result: dict = {}
