from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from models.db import Message, User, engine
from server.auth import SECRET_KEY, ALGORITHM

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


@router.websocket("/ws/{username}")
async def websocket_endpoint(
    username: str,
    websocket: WebSocket,
    token: str = Query(...),
):
    # 1. Verify JWT BEFORE accepting the connection
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        token_username = payload.get("sub")
        if token_username != username:
            await websocket.close(code=1008)
            return
    except JWTError:
        await websocket.close(code=1008)
        return

    # 2. Accept only after verification
    await manager.connect(username, websocket)

    # 3. Open one DB session for the lifetime of this connection
    with Session(engine) as db:
        try:
            while True:
                data = await websocket.receive_json()

                to_user = data.get("to")
                ciphertext = data.get("ciphertext")

                # Guard against malformed messages
                if not to_user or not ciphertext:
                    continue

                delivered = await manager.send_to(
                    to_user,
                    {"from": username, "ciphertext": ciphertext}
                )

                # If recipient is offline, save to DB for later
                if not delivered:
                    sender = db.query(User).filter(User.username == username).first()
                    recipient = db.query(User).filter(User.username == to_user).first()
                    if sender and recipient:
                        msg = Message(
                            sender_id=sender.id,
                            recipient_id=recipient.id,
                            ciphertext=bytes.fromhex(ciphertext),
                        )
                        db.add(msg)
                        db.commit()

        except WebSocketDisconnect:
            manager.disconnect(username)