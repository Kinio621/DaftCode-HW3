from hashlib import sha256
from fastapi import FastAPI, Response, Cookie, HTTPException, status, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from starlette.responses import RedirectResponse

import secrets

app = FastAPI()

app.secret_key = "very constatn and random secret, best 64 characters"
app.sessions={}
app.users={"trudnY":"PaC13Nt"}
security = HTTPBasic()

def verify(credentials: HTTPBasicCredentials = Depends(security)):
    if (secrets.compare_digest(credentials.username, "trudnY") and secrets.compare_digest(credentials.password, "PaC13Nt")):
        session_token = sha256(bytes(f"{credentials.username}{credentials.password}{app.secret_key}", encoding='utf8')).hexdigest()
        app.sessions[session_token]=credentials.username
        return session_token

    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect login or password",
            headers={"WWW-Authenticate": "Basic"},
        )
   
@app.post("/login")
def login(response: Response, session_token: str = Depends(verify)):
    response.status_code = status.HTTP_302_FOUND
    response.headers["Location"] = "/welcome"
    response.set_cookie(key="session_token", value=session_token)

@app.get("/welcome")
def welcome():
    return {"message": "Hello there"}

@app.get("/")
def default():
    return {"message": "Hello there"}
