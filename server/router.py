from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from models.db import Message, User, engine
from server.auth import SECRET_KEY, ALGORITHM
from sqlalchemy import and_, or_
from datetime import datetime, timezone

from crypto.key_exchange import load_private_key, deserialize_public_key, ecdh
from crypto.key_derivation import derive
from crypto.encryption import encrypt, decrypt
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

router = APIRouter()


class ConnectionManager:
    def __init__(self):
        self.active: dict[str, dict] = {}

    async def connect(self, username: str, ws: WebSocket, client: str):
        await ws.accept()
        self.active[username] = {"ws": ws, "client": client}

    def disconnect(self, username: str):
        self.active.pop(username, None)

    async def send_to(self, username: str, message: dict) -> bool:
        connection = self.active.get(username)
        if not connection:
            return False
        try:
            await connection["ws"].send_json(message)
            return True
        except Exception:
            self.disconnect(username)
            return False


manager = ConnectionManager()


@router.get("/ws-test")
def ws_test():
        return {"ok": True}

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str = Query(...), client: str = Query("web")):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        token_username = payload.get("sub")
        if token_username is None:
            raise JWTError()
    except JWTError:
        await websocket.close(code=1008)
        return

    await manager.connect(token_username, websocket, client)

    with Session(engine) as db:
        try:
            while True:
                data = await websocket.receive_json()
                to_user = data.get("to")
                if not to_user:
                    continue

                sender = db.query(User).filter(User.username == token_username).first()
                recipient = db.query(User).filter(User.username == to_user).first()
                if not sender or not recipient:
                    continue

                ciphertext = b""
                
                if client == "web":
                    plaintext = data.get("plaintext")
                    if not plaintext:
                        continue
                    
                    try:
                        my_priv, my_pub = load_private_key(f"{token_username}_private_key.pem")
                        their_pub = deserialize_public_key(recipient.public_key)
                        
                        shared_secret = ecdh(my_priv, their_pub)
                        my_pub_raw = my_pub.public_bytes(Encoding.Raw, PublicFormat.Raw)
                        their_pub_raw = their_pub.public_bytes(Encoding.Raw, PublicFormat.Raw)
                        
                        aes_key = derive(shared_secret, my_pub_raw, their_pub_raw)
                        ciphertext = encrypt(aes_key, plaintext.encode('utf-8'))
                    except Exception as e:
                        print(f"Encryption failed for web client: {e}")
                        continue
                else:
                    ciphertext_hex = data.get("ciphertext")
                    if not ciphertext_hex:
                        continue
                    try:
                        ciphertext = bytes.fromhex(ciphertext_hex)
                    except ValueError:
                        continue

                sender = db.query(User).filter(User.username == token_username).first()
                recipient = db.query(User).filter(User.username == to_user).first()
                if not sender or not recipient:
                    continue

                # fix 2: this now actually runs
                is_new_chat = not db.query(Message).filter(
                    or_(
                        and_(Message.sender_id == sender.id, Message.recipient_id == recipient.id),
                        and_(Message.sender_id == recipient.id, Message.recipient_id == sender.id)
                    )
                ).first()

                # Always save message to DB for history
                db.add(Message(sender_id=sender.id, recipient_id=recipient.id, ciphertext=ciphertext, timestamp=datetime.now(timezone.utc)))
                db.commit()

                recipient_conn = manager.active.get(to_user)
                delivered = False
                if recipient_conn:
                    if recipient_conn["client"] == "web":
                        try:
                            rec_priv, rec_pub = load_private_key(f"{to_user}_private_key.pem")
                            sen_pub = deserialize_public_key(sender.public_key)
                            
                            shared_secret = ecdh(rec_priv, sen_pub)
                            rec_pub_raw = rec_pub.public_bytes(Encoding.Raw, PublicFormat.Raw)
                            sen_pub_raw = sen_pub.public_bytes(Encoding.Raw, PublicFormat.Raw)
                            
                            aes_key = derive(shared_secret, rec_pub_raw, sen_pub_raw)
                            decrypted_text = decrypt(aes_key, ciphertext).decode('utf-8')
                            
                            delivered = await manager.send_to(
                                to_user,
                                {"type": "message", "from": token_username, "plaintext": decrypted_text}
                            )
                        except Exception as e:
                            print(f"Decryption failed for web client: {e}")
                    else:
                        delivered = await manager.send_to(
                            to_user,
                            {"type": "message", "from": token_username, "ciphertext": ciphertext.hex()}
                        )

                if is_new_chat:
                    await manager.send_to(to_user, {"type": "new_chat", "data": {"recipient_id": sender.id, "username": token_username}})
                    await manager.send_to(token_username, {"type": "new_chat", "data": {"recipient_id": recipient.id, "username": to_user}})

        except WebSocketDisconnect:
            manager.disconnect(token_username)
