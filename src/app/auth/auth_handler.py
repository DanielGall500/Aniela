from typing import Dict
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
import sqlite3

auth_db = sqlite3.connect("app/auth/authentication.sqlite")
cursor = auth_db.cursor()
ph = PasswordHasher()

def authenticate_user(username: str, password: str) -> Dict:
    # the output of this validation
    validation_results = {
        "validated": False,
        "error": "None"
    }

    try:
        password_query = get_password_query(username)

        if(password_query["exists"]):
            hash = password_query["hash"]

            # verify that the hash password is the same as the 
            # provided password for this user.
            is_valid_login = ph.verify(hash, password)

            # if no VerifyMismatchError has been caught,
            # then we are free to sign and send off the token.
            validation_results["validated"] = is_valid_login
        else:
            validation_results["error"] = "User not found."
    except VerifyMismatchError:
        validation_results["error"] = "Invalid credentials."
    return validation_results


def validate_username(username: str):
    username_query = cursor.execute("SELECT username FROM users WHERE username='{username}';").fetchone()
    return username_query != None


def get_password_query(username: str):
    pass_query = cursor.execute(f"SELECT password FROM users WHERE username='{username}';").fetchone()
    pass_exists = pass_query != None
    if(pass_exists):
        pass_hash = pass_query[0]
        return {"exists": pass_exists, "hash": pass_hash}
    else:
        return {"exists": pass_exists}
