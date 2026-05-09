from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.hash import argon2
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, scoped_session, sessionmaker
from models.db import User, engine
import os
from fastapi import HTTPException, status

router = APIRouter(prefix="/auth", tags=["Authentication"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

SECRET_KEY = os.environ.get("SECRET_KEY", "change-this-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def get_db():
    # yield a Session, close it after the request
            # Create a SQLAlchemy session
              with Session(engine) as db:
                try:
                    yield db
                    db.commit()
                except Exception:
                    db.rollback()
                    raise
#everytime am registering or loging in i need a db session which is by the function above
#if it goes well the db.commit means it will save changes to db , other wise it will rollback

def create_access_token(data: dict) -> str:
    # copy data , shallow copy if we modify to_encode then data won't change
    to_encode = data.copy()
    # add "exp" key with expiry time 30 mins
    expire = datetime.now(timezone.utc) + timedelta(minutes=30)
    #adds a new key-value pair to the dictionary , adds another attribute to it
    to_encode.update({"exp": expire})
    # return jwt.encode(...)
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    ...

# depending on 0auth2 is what extracts token from http header
def verify_token(token: str = Depends(oauth2_scheme)) -> str:
    # decode the JWT
    token_data = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    # extract username from payload["sub"]
    username: str = token_data["username"]
    # raise HTTPException(401) if invalid or expired
    if username is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    return username
    ...


@router.post("/register", status_code=201)
async def register(
    username: str,
    email: str,
    password: str,
    public_key: str,
    db: Session = Depends(get_db)
):

    existing_user = db.query(User).filter(User.username == username).first()
    if existing_user is None:
        new_user = User(
            username=username,
            email=email,
            password_hash=argon2.hash(password.encode("utf-8")),
            public_key=public_key.encode("utf-8"),
        )
        db.add(new_user)
        db.commit()

        return {"message": "registered"}
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