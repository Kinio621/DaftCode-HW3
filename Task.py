from fastapi import FastAPI

app = FastAPI()

@app.get("/welcome")
def root():
    return {"message": "Hello there"}

@app.get("/")
def root():
    return {"message": "Hello there"}
