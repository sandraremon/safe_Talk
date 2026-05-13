from sqlalchemy import and_, or_
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
import os
from crypto.encryption import encrypt, decrypt
from crypto.key_exchange import load_private_key, deserialize_public_key, ecdh
from crypto.key_derivation import derive
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
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
async def get_conversations(db: Session = Depends(get_db), current_user: str = Depends(verify_token)):
    user = db.query(User).filter(User.username == current_user).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    partner_ids = {id for (id,) in db.query(Message.recipient_id)
                   .filter(Message.sender_id == user.id)
                   .union(db.query(Message.sender_id)
                   .filter(Message.recipient_id == user.id))}

    partners = db.query(User).filter(User.id.in_(partner_ids)).all()
    return [{"recipient_id": p.id, "username": p.username} for p in partners]


@router.get("/{username}")
async def get_public_key(
    username: str,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"username": username, "public_key": user.public_key}

#this is for the frontend to get a contact from the DB to text them
@router.get("/users/search")
async def search_users(
    user: str,
    db: Session = Depends(get_db),
    current_user: str = Depends(verify_token)
):
    current_user = db.query(User).filter(User.username == current_user).first()

    users = db.query(User).filter(User.username.ilike(f"%{user}%"),
        User.username != current_user.username,
    ).union(db.query(User).filter(User.email.ilike(f"%{user}%"), User.email != current_user.email)).all()


    return [{"username": u.username} for u in users]

@router.get("/messages/{username}")
async def get_messages(
    username: str,
    db: Session = Depends(get_db),
    current_user: str = Depends(verify_token),
    client: str = "web"
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

    # Fix #7: build a {id -> username} map so frontend gets a string, not an integer
    name_map = {me.id: me.username, them.id: them.username}
    
    results = []
    aes_key = None
    
    if client == "web":
        try:
            my_priv, my_pub = load_private_key(f"{current_user}_private_key.pem")
            their_pub = deserialize_public_key(them.public_key)
            shared_secret = ecdh(my_priv, their_pub)
            my_pub_raw = my_pub.public_bytes(Encoding.Raw, PublicFormat.Raw)
            their_pub_raw = their_pub.public_bytes(Encoding.Raw, PublicFormat.Raw)
            aes_key = derive(shared_secret, my_pub_raw, their_pub_raw)
        except Exception as e:
            print(f"Failed to derive key for history: {e}")

    for msg in messages:
        sender_name = name_map.get(msg.sender_id, str(msg.sender_id))
        
        if client == "web":
            plaintext = "[Decryption Failed]"
            if aes_key:
                try:
                    plaintext = decrypt(aes_key, msg.ciphertext).decode('utf-8')
                except Exception:
                    pass
            results.append({
                "from": sender_name,
                "plaintext": plaintext,
                "timestamp": msg.timestamp.isoformat()
            })
        else:
            results.append({
                "from": sender_name,
                "ciphertext": msg.ciphertext.hex(),
                "timestamp": msg.timestamp.isoformat()
            })

    return results

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

