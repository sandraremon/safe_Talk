from sqlalchemy import and_, or_

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from fastapi import APIRouter

import os
from datetime import datetime
from crypto.encryption import encrypt
from models.db import Message, User, engine
from server.auth import get_db, verify_token

router = APIRouter()

#this returns the new public key not the one made in registration
@router.put("/update")
async def update_public_key(
        payload: dict,
        db: Session = Depends(get_db),
        current_user: str = Depends(verify_token)
):
    user = db.query(User).filter(User.username == current_user).first()
    user.public_key = payload["public_key"]
    db.commit()
    return {"message": "key updated"}


@router.get("/mydetails")
async def get_my_details(
        db: Session = Depends(get_db),
        current_user: str = Depends(verify_token)
):
    print("HELLLLLLLO")
    user = db.query(User).filter(User.username == current_user).first()
    print(user)
    print(current_user)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"username": user.username, "email": user.email}


@router.get("/conversations")
async def get_conversations(
    db: Session = Depends(get_db),
    current_user: str = Depends(verify_token)
):
    user = db.query(User).filter(User.username == current_user).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    sent_to = db.query(Message.recipient_id).filter(Message.sender_id == user.id)
    received_from = db.query(Message.sender_id).filter(Message.recipient_id == user.id)
    
    chat_partner_ids = sent_to.union(received_from).all()
    chat_partner_ids = [r[0] for r in chat_partner_ids]

    partners = db.query(User).filter(User.id.in_(chat_partner_ids)).all()

    return [
        {
            "recipient_id": p.id,
            "recipient_name": p.username,
        }
        for p in partners
    ]

@router.get("/{username}")
async def get_public_key(
    username: str,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"username": username, "public_key": user.public_key}

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
            "from": msg.sender_id,
            "ciphertext": msg.ciphertext.hex(),
            "timestamp": msg.timestamp.isoformat()
        }
        for msg in messages
    ]


@router.post("/sendMessage")
async def send_message(
    plaintext: str,
    username: str,
    db: Session = Depends(get_db),
    current_user: str = Depends(verify_token)
):
    sender = db.query(User).filter(User.username == current_user).first()
    recipient = db.query(User).filter(User.username == username).first()

    if not sender:
        raise HTTPException(status_code=404, detail="Sender not found")

    if not recipient:
        raise HTTPException(status_code=404, detail="Recipient not found")

    message = Message(
        sender_id=sender.id,
        recipient_id=recipient.id,
        ciphertext=encrypt(os.urandom(32), plaintext.encode("utf-8"))
    )

    db.add(message)
    db.commit()

    return {"message": "Message sent successfully"}