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

def login_check_cred(credentials: HTTPBasicCredentials = Depends(security)):
    correct = False
    for username, password in app.users.items():
        correct_username = secrets.compare_digest(credentials.username, username)
        correct_password = secrets.compare_digest(credentials.password, password)
        if (correct_username and correct_password):
            correct = True
    if not correct:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect login or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    session_token = sha256(bytes(f"{credentials.username}{credentials.password}{app.secret_key}", encoding='utf8')).hexdigest()
    app.sessions[session_token]=credentials.username
    return session_token

@app.post("/login")
def login(response: Response, session_token: str = Depends(login_check_cred)):
    response.status_code = status.HTTP_302_FOUND
    response.headers["Location"] = "/welcome"
    response.set_cookie(key="session_token", value=session_token)

@app.get("/welcome")
def welcome():
    return {"message": "Hello there"}

@app.get("/")
def default():
    return {"message": "Hello there"}
