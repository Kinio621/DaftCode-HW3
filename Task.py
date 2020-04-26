from hashlib import sha256
from fastapi import FastAPI, Response, Request, Cookie, HTTPException, status, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from starlette.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

import secrets

app = FastAPI()

app.secret_key = "very constatn and random secret, best 64 characters"
app.sessions={}
app.users={"trudnY":"PaC13Nt"}
app.last_patient_id=0
app.patients={}
security = HTTPBasic()
templates = Jinja2Templates(directory="templates")

MESSAGE_UNAUTHORIZED = "Log in to access this page."

class Patient(BaseModel):
    name: str
    surename: str

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

@app.post("/patient")
def add_patient(response: Response, rq: Patient, session_token: str = Depends(verify_cookie)):
    if session_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not logged in user",
        )
    id=f"id_{app.last_patient_id}"
    app.last_patient_id+=1
    app.patients[id]=rq.dict()
    response.status_code = status.HTTP_302_FOUND
    response.headers["Location"] = f"/patient/{id}"

@app.get("/patient")
def get_all_patients(response: Response, session_token: str = Depends(verify_cookie)):
    if session_token is None:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return MESSAGE_UNAUTHORIZED
    if len(app.patients) != 0:
        return app.patients
    response.status_code = status.HTTP_204_NO_CONTENT

@app.get("/patient/{pid}")
def get_patient(pid: str, response: Response, session_token: str = Depends(verify_cookie)):
    if session_token is None:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return MESSAGE_UNAUTHORIZED
    if pid in app.patients:
        return app.patients[pid]
    response.status_code = status.HTTP_204_NO_CONTENT

@app.delete("/patient/{pid}")
def remove_patient(pid: str, response: Response, session_token: str = Depends(verify_cookie)):
    if session_token is None:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return MESSAGE_UNAUTHORIZED
    app.patients.pop(pid, None)
    response.status_code = status.HTTP_204_NO_CONTENT

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
def welcome(request: Request, response: Response, session_token: str = Depends(verify_cookie)):
    if session_token is None:
       raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not logged in user",
        )
    return templates.TemplateResponse("welcome.html", {"request": request, "user": "trudnY"})

@app.get("/")
def default():
    return {"message": "Hello there"}
