from operator import and_, or_

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from fastapi import APIRouter


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


@router.get("/{username}")
async def get_public_key(
    username: str,
    db: Session = Depends(get_db),
    current_user: str = Depends(verify_token)
):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"username": username, "public_key": user.public_key}


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
