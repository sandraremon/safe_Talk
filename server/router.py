from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from models.db import Message, User, engine
from server.auth import SECRET_KEY, ALGORITHM
from sqlalchemy import and_, or_

router = APIRouter()


class ConnectionManager:
    def __init__(self):
        self.active: dict[str, WebSocket] = {}

    async def connect(self, username: str, ws: WebSocket):
        await ws.accept()
        self.active[username] = ws

    def disconnect(self, username: str):
        self.active.pop(username, None)

    async def send_to(self, username: str, message: dict) -> bool:
        ws = self.active.get(username)
        if not ws:
            return False
        try:
            await ws.send_json(message)
            return True
        except Exception:
            self.disconnect(username)
            return False


manager = ConnectionManager()


@router.websocket("/ws")
async def websocket_endpoint(
    # username: str,
    websocket: WebSocket,
    token: str = Query(...),
):
    # 1. Verify JWT BEFORE accepting the connection
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        token_username = payload.get("sub")
        if token_username is None:
            raise JWTError()
    
    except JWTError:
        await websocket.close(code=1008)
        return

    # 2. Accept only after verification
    await manager.connect(token_username, websocket)

    # 3. Open one DB session for the lifetime of this connection
    with Session(engine) as db:
        try:
            while True:
                data = await websocket.receive_json()

                to_user = data.get("to")
                #ciphertext = data.get("ciphertext")
                text= data.get("text") #bcuz its coming from front as plain

                # Guard against malformed messages
                if not to_user or not text:
                    continue

                sender = db.query(User).filter(User.username == token_username).first()
                recipient = db.query(User).filter(User.username == to_user).first()
                if not sender or not recipient:
                    continue
                    # Check if this is the first message between them
                existing = db.query(Message).filter(
                     or_(
                        and_(Message.sender_id == sender.id, Message.recipient_id == recipient.id),
                        and_(Message.sender_id == recipient.id, Message.recipient_id == sender.id)
                    )
                ).first()
                is_new_chat = existing is None

                delivered = await manager.send_to(
                    to_user,
                    {"type": "message","from": token_username, "text": text}
                )

                # If recipient is offline, save to DB for later
                if not delivered:
                    sender = db.query(User).filter(User.username == token_username).first()
                    recipient = db.query(User).filter(User.username == to_user).first()
                    if sender and recipient:
                        msg = Message(
                            sender_id=sender.id,
                            recipient_id=recipient.id,
                            ciphertext=text.encode("utf-8"),
                        )
                        db.add(msg)
                        db.commit()
                # Push new_chat event to BOTH users if this is their first message
                if is_new_chat:
                      await manager.send_to(to_user, {
                            "type": "new_chat",
                            "data": {"recipient_id": sender.id, "username": token_username}
                      })
                      await manager.send_to(token_username, {
                             "type": "new_chat",
                             "data": {"recipient_id": recipient.id, "username": to_user}
                      })

        except WebSocketDisconnect:
            manager.disconnect(token_username)