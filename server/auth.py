from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from pydantic import BaseModel
import bcrypt
#from passlib.hash import argon2
from sqlalchemy.orm import Session
from sqlalchemy.sql.functions import current_user

from  crypto.key_exchange import generate_keypair, save_private_key, serialize_public_key

from models.db import User, engine
import os
from passlib.context import CryptContext
from dotenv import load_dotenv

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable is not set. Please check your .env file.")

# No prefix here — main.py adds /auth when including the router
router = APIRouter(tags=["Authentication"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# SECRET_KEY = os.environ.get("SECRET_KEY", "change-this-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def get_db():
    """Yields a database session and handles transaction management."""
    with Session(engine) as db:
        try:
            yield db
            db.commit()
        except Exception:
            db.rollback()
            raise
#everytime  am registering or loging in i need a db session which is by the function above
#if it goes well the db.commit means it will save changes to db , other wise it will rollback

def create_access_token(data: dict) -> str:
    # copy data , shallow copy if we modify to_encode then data won't change
    to_encode = data.copy()
    # add "exp" key with expiry time 30 mins
    expire = datetime.now(timezone.utc) + timedelta(minutes=3000)
    #adds a new key-value pair to the dictionary , adds another attribute to it
    to_encode.update({"exp": expire})
    # return jwt.encode(...)
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# depending on 0auth2 is what extracts token from http header
def verify_token(token: str = Depends(oauth2_scheme)) -> str:
    try:
    # decode the JWT

        token_data = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # extract username from payload["sub"]
        username: str = token_data["sub"]
        # raise HTTPException(401) if invalid or expired
        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
        return username
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid or expired token")


class RegisterModel(BaseModel):
    username: str
    password: str
    email: str

@router.post("/register", status_code=201)
async def register(
    user: RegisterModel,
    db: Session = Depends(get_db)
):
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists")
    
    # Check if user already exists
    existing_email = db.query(User).filter(User.email == user.email).first()
    if existing_email is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    
    private_key, public_key = generate_keypair()
    public_hex = serialize_public_key(public_key)
    new_user = User(
        username=user.username,
        email=user.email,
        password_hash=bcrypt.hashpw(user.password.encode("utf-8"), bcrypt.gensalt()),
        public_key=public_hex
    )
    save_private_key(private_key, path=f"{user.username}_private_key.pem")
    db.add(new_user)
    db.commit()

    # Return token for new user
    token = create_access_token(data={"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}

@router.post("/login", status_code=201)
async def login(
     form_data: OAuth2PasswordRequestForm = Depends(),
     db: Session = Depends(get_db)
):

    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not bcrypt.checkpw(form_data.password.encode(), user.password_hash.encode()):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")

    token = create_access_token(data={"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}
