from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.hash import argon2
from sqlalchemy.orm import Session
from models.db import User, engine
import os

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

SECRET_KEY = os.environ.get("SECRET_KEY", "change-this-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def get_db():
    # yield a Session, close it after the request
    ...


def create_access_token(data: dict) -> str:
    # copy data, add "exp" key with expiry time
    # return jwt.encode(...)
    ...


def verify_token(token: str = Depends(oauth2_scheme)) -> str:
    # decode the JWT
    # extract username from payload["sub"]
    # raise HTTPException(401) if invalid or expired
    # return username
    ...


@router.post("/register", status_code=201)
async def register(
    username: str,
    email: str,
    password: str,
    public_key: str,
    db: Session = Depends(get_db)
):
    # 1. check username/email not already taken
    # 2. hash the password with argon2.hash()
    # 3. create User object, add to db, commit
    # 4. return {"message": "registered"}
    ...


@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    # 1. look up user by username
    # 2. argon2.verify(form_data.password, user.password_hash)
    # 3. if invalid raise HTTPException(401)
    # 4. create_access_token({"sub": user.username})
    # 5. return {"access_token": token, "token_type": "bearer"}
    ...