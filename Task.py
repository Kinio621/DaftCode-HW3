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
def add_patient(response: Response, request: Patient, session_token: str = Depends(verify_cookie)):
    if session_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not logged in user",
        )
    id=app.last_patient_id
    app.last_patient_id+=1
    app.patients[id]=request.dict()
    response.status_code = status.HTTP_302_FOUND
    response.headers["Location"] = f"/patient/{id}"

@app.get("/patient")
def all_patients(response: Response, session_token: str = Depends(verify_cookie)):
    if session_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not logged in user",
        )
    return app.patients

@app.get("/patient/{id}")
def get_patient(id: str, response: Response, session_token: str = Depends(verify_cookie)):
    if session_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not logged in user",
        )
    if id in app.patients:
        return app.patients[id]
    else:
        raise HTTPException(
            status_code=status.HTTP_204_NO_CONTENT,
            detail="No patient with such id",
        )

@app.delete("/patient/{id}")
def delete_patient(id: str, response: Response, session_token: str = Depends(verify_cookie)):
    if session_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not logged in user",
        )
    if id in app.patients:
        app.patients.pop(id)
    else:
        raise HTTPException(
            status_code=status.HTTP_204_NO_CONTENT,
            detail="No patient with such id",
        )

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
