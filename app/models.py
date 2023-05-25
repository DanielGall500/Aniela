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

class DeleteRequest(BaseModel):
    src: str = Field(description="The source language.")
    tgt: str = Field(description="The target language.")
    model_id: str = Field(description="The unique ID of the model you wish to delete.")

class AddRequest(BaseModel):
    src: str = Field(description="The source language.")
    tgt: str = Field(description="The target language.")
    server: str = Field(description="The name of the server that the model is being hosted on. " + 
                    "This name should correspond to an IP and port in your environment variables.")
    gpu: str = Field(description="The id of the GPU that you would like to use .")
    id: str = Field(description="The unique ID of the model you wish to add.")