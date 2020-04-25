from hashlib import sha256
from fastapi import FastAPI, Response, Cookie, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials

app = FastAPI()

@app.post("/login")
def login(credentials: HTTPBasicCredentials = HTTPBasic()):
    if(secrets.compare_digest(credentials.username, "trudnY") and secrets.compare_digest(credentials.password, "PaC13Nt")):
        response=RedirectResponse(url='/welcome')
        return response
    else:
        raise HTTPException(status=401, detail='failed to log in')

@app.get("/welcome")
def welcome():
    return {"message": "Hello there"}

@app.get("/")
def default():
    return {"message": "Hello there"}
