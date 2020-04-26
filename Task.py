from hashlib import sha256
from fastapi import FastAPI, Response, Request, Cookie, HTTPException, status, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from starlette.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

import secrets

app = FastAPI()

app.secret_key = "very constatn and random secret, best 64 characters"
app.sessions={}
app.users={"trudnY":"PaC13Nt"}
security = HTTPBasic()
template = Jinja2Templates(directory="templates")

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
def verify_cookie(session_token: str = Cookie(None)):
    if session_token not in app.sessions:
        session_token = None
    return session_token

@app.post("/login")
def login(response: Response, session_token: str = Depends(verify)):
    response.status_code = status.HTTP_302_FOUND
    response.headers["Location"] = "/welcome"
    response.set_cookie(key="session_token", value=session_token)

@app.post("/logout")
def logout(response: Response, session_token: str = Depends(verify_cookie)):
    if session_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not logged in user",
        )
    response.status_code = status.HTTP_302_FOUND
    response.headers["Location"] = "/"
    app.sessions.pop(session_token)

@app.get("/welcome")
def welcome(request: Request, response: Response, session_token: str = Depends(check_cookie)):
    if session_token is None:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return MESSAGE_UNAUTHORIZED
    username = app.sessions[session_token]
    return templates.TemplateResponse("welcome.html", {"request": request, "user": username})

@app.get("/")
def default():
    return {"message": "Hello there"}
