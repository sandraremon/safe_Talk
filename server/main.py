from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from models.db import Base, engine
from server.auth import router as auth_router
from server.key_store import router as key_router
from server.router import router as ws_router
from client.session import Session
import asyncio

app = FastAPI(title="SafeTalk")

# Allow browser clients to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(engine)

app.include_router(auth_router, prefix="/auth")
app.include_router(key_router, prefix="/key")
app.token_url = "/login"
app.include_router(auth_router)
app.include_router(key_router)
app.include_router(ws_router)