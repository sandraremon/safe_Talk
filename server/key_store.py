import os
from operator import and_, or_

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import text, select
from sqlalchemy.orm import Session, defer
from fastapi import APIRouter

from crypto.encryption import encrypt
from models.db import Message, User, engine
from server.auth import get_db, verify_token

router = APIRouter()


@router.get("/keys/{username}")
async def get_public_key(
    username: str,
    db: Session = Depends(get_db),
    current_user: str = Depends(verify_token)
):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"username": username, "public_key": user.public_key.hex()}


# 
@router.get("/messages/{username}")
async def get_message_history(
    username: str,
    db: Session = Depends(get_db),
    current_user: str = Depends(verify_token)
):
    me = db.query(User).filter(User.username == current_user).first()
    them = db.query(User).filter(User.username == username).first()
 
    if not them:
        raise HTTPException(status_code=404, detail="User not found")
 
    messages = db.query(Message).filter(
        or_(
            and_(Message.sender_id == me.id, Message.recipient_id == them.id),
            and_(Message.sender_id == them.id, Message.recipient_id == me.id)
        )
    ).order_by(Message.timestamp).all()
 
    return [
        {
            "from": msg.sender.username,
            "ciphertext": msg.ciphertext.hex(),
            "timestamp": msg.timestamp.isoformat()
        }
        for msg in messages
    ]

@router.get("/conversations")
async def get_user_conversations(
        db: Session = Depends(get_db),
        current_user: str = Depends(verify_token)
):
    me = db.query(User).filter(User.username == current_user).first()
    conversations = (
        db.query(User.id, User.username)
        .join(Message, User.id == Message.recipient_id)
        .filter(Message.sender_id == me.id)
        .distinct(Message.recipient_id)
        .all()
    )

    result = [
        {
            "recipient_id": recipient_id,
            "recipient_name": recipient_name
        }
        for recipient_id, recipient_name in conversations
    ]

    print("hello    ")
    print(result)
    print("hello again    ")

    return result

@router.post("/sendMessage")
async def get_user_conversations(
        plaintext: str,
        to_user: int,
        db: Session = Depends(get_db),
        current_user: str = Depends(verify_token)
):
    db.add(Message(
        sender_id = db.query(User).filter(current_user == User.username).first().id,
        recipient_id = db.query(User).filter(User.id == to_user).first().id,
        ciphertext = encrypt(os.urandom(32), plaintext.encode("utf-8"))
    ))
    db.commit()