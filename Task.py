from hashlib import sha256
from fastapi import FastAPI, Response, Cookie, HTTPException, status, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from starlette.responses import RedirectResponse

import secrets

app = FastAPI()

app.secret_key = "very constatn and random secret, best 64 characters"
app.tokens_list = []
security = HTTPBasic()

def verify(credentials: HTTPBasicCredentials = Depends(security)):
    if(secrets.compare_digest(credentials.username, "trudnY") and secrets.compare_digest(credentials.password, "PaC13Nt")):
        return credentials.username
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='wrong username or password')

@app.post("/login")
def login(user:str, passwd: str, response: Response, verify_user = Depends(verify)):
     session_token = sha256(bytes(f"{user}{passwd}{app.secret_key}", encoding='utf8')).hexdigest()
     app.tokens_list.append(session_token)

     response.set_cookie(key="session_token", value=session_token)
     response = RedirectResponse(url = "/welcome")
     return response

@app.get("/welcome")
def welcome():
    return {"message": "Hello there"}

@app.get("/")
def default():
    return {"message": "Hello there"}
