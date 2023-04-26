from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Request, HTTPException
from dotenv import dotenv_values
from typing import Dict
import time
import jwt

# -- JWT Configuration Variables --
app_config = dotenv_values('app/.env')
JWT_SECRET = app_config["SECRET_KEY"]
JWT_ALGORITHM = app_config["JWT_ALGORITHM"]
JWT_EXPIRY_PERIOD = 48 # hours

# -- Handle JSON Web Tokens --
# The below classes and functions are used to sign and decode JSON web
# tokens to be passed between the API and the user.
# Using the secret key, we can verify that a token is authentic and the
# user making a request was given permission to do so.

# -- JWT Bearer: verifies the authenticity of a JWT from a user --
class JWTBearer(HTTPBearer):
    current_user = None
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)

        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(status_code=403, detail="Invalid authentication scheme.")
            if not self.verifyJWT(credentials.credentials):
                raise HTTPException(status_code=403, detail="Invalid token or expired token.")
            return credentials.credentials
        else:
            raise HTTPException(status_code=403, detail="Invalid authorization code.")

    def verifyJWT(self, token: str):
        is_valid_token = False
        username = None

        # first check if a token has been provided
        if not token:
            return is_valid_token
        else:
            # decode the token using the secret key
            try:
                decoded_token = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
                is_valid_token = True
                username = decoded_token["username"]
            except: 
                is_valid_token = False
        self.current_user = username
        return is_valid_token

# -- signJWT: create a payload for a JWT and sign it using the secret key --
def signJWT(username: str) -> Dict[str, str]:
    payload = {
        "username": username,
        "expires": time.time() + (JWT_EXPIRY_PERIOD * 60 * 60)
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token
