# app/main.py
from fastapi import FastAPI
from app.routers import auth_routes

app = FastAPI()

app.include_router(auth_routes.router, prefix="/auth", tags=["auth"])

@app.get("/")
async def root():
    return {"message": "Welcome to the FastAPI Authentication Microservice"}