from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
from fastapi import APIRouter


from models.db import Message, User, engine
from server.auth import verify_token

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active: dict[str, WebSocket] = {}

    async def connect(self, username: str, ws: WebSocket):
        # accept the WebSocket
        await ws.accept()
        # store in self.active
        self.active[username] = ws

    def disconnect(self, username: str):
        # remove from self.active
        self.active.pop(username, None)

    async def send_to(self, username: str, message: dict):
        # look up self.active[username]
        ws = self.active.get(username)
        # if online: await ws.send_json(message)
        if not ws:
            return False
        try:
            await ws.send_json(message)
            print(f"Sent to {username}")
            return True
        except Exception as e:
            print(f"Error sending to {username}:", e)
            self.disconnect(username)
            return False
        # if offline: return False so caller saves to DB
        
            
        
        ...


manager = ConnectionManager()


@router.websocket("/ws/{username}")
async def websocket_endpoint(
    username: str,
    websocket: WebSocket,
    token:str=Query(...),
    db: Session = Depends(verify_token)  # how will you get the username from the token? how will you verify it?
    # how will you verify the JWT over a WebSocket connection?
):
    await manager.connect(username, websocket)
    # ⚠️ create DB session manually (Depends doesn't work in websockets)
    db: Session = Session(bind=engine)
    try:
        while True:
            data = await websocket.receive_json()
            # data has "to" and "ciphertext"
            to_user = data.get("to")
            ciphertext = data.get("ciphertext")
            message_data = {
                "from": username,
                "to": to_user,
                "ciphertext": ciphertext,
            }
            # forward to recipient
            sent = await manager.send_to(to_user, message_data)
            # if offline, save to DB
            if not sent:
                msg = Message(
                    sender=username,
                    receiver=to_user,
                    ciphertext=ciphertext
                )
                db.add(msg)
                db.commit()
    except WebSocketDisconnect:
        manager.disconnect(username) 