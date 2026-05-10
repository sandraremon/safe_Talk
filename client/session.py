import json
from typing import Callable, Optional
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

import httpx
import websockets
from pathlib import Path
from websockets.exceptions import ConnectionClosedError, ConnectionClosedOK

from crypto.key_exchange import (
    generate_keypair,
    save_private_key,
    load_private_key,
    serialize_public_key,
    deserialize_public_key,
    ecdh,
)
from crypto.key_derivation import derive
from crypto.encryption import encrypt, decrypt


class Session:
#this is Asymmetric Encryption because my private is in the machine disk in .pem
    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        ws_url: str = "ws://localhost:8000",
    ):
        self.base_url = base_url
        self.ws_url = ws_url
        #this is the digital identity , it checks a .pem file in computer
        if Path("private_key.pem").exists():
            self.private_key = load_private_key("private_key.pem")
            self.public_key = self.private_key.public_key()

        else:
            self.private_key, self.public_key = generate_keypair()
            save_private_key(self.private_key)

        self.username= None
        self.token = None
        self._ws  = None
        #This is a placeholder for a callback function
        self._on_message= None
        #the shared AES key
        self._session_keys={}

        self.http= httpx.Client()
        pass


    def register(self, username: str, email: str, password: str) -> None:
        #save the identity of user upon registration
        save_private_key(self.private_key)
        #get the public key but first serialize for the server to store
        public_hex = serialize_public_key(self.public_key)
        resp = self.http.post(
            f"{self.base_url}/auth/register",
            params={
                "username": username,
                "email": email,
                "password": password,
                "public_key": public_hex,
            }
        )
        self._do_login(username, password)


    def login(self, username: str, password: str) -> None:
      self._do_login(username, password)

# to match the login function in server , the OAuth thing expects form-encoded data , not json nor params
#Content-Type : application/x-www-form-urlencoded,
    def _do_login(self, username: str, password: str) -> None:
        resp = self.http.post(
            f"{self.base_url}/auth/login",
            data={"username": username, "password": password} )
        self._raise(resp)
        self.token = resp.json()["access_token"]
        self.username = username

#contact is the person i wanna contact and talk to
    def start_chat(self, contact: str) -> None:
        #if i already have this contact before then just return the secrete key
         # from session keys
        if contact in self._session_keys:
            return

        #if i don't then am getting their data from header to get their public key
        #to then create our shared secret key
        resp = self.http.get(
            f"{self.base_url}/keys/{contact}",
            headers=self._auth_headers()
        )
        self._raise(resp)

        # convert it from string to hec
        their_pub = deserialize_public_key(resp.json()["public_key"])
        #making the shared key
        shared_secret = ecdh(self.private_key, their_pub)

        # making my public key and my contacts back to hex to derive it so its more secure
        my_pub_raw = self.public_key.public_bytes(Encoding.Raw, PublicFormat.Raw)
        their_pub_raw = their_pub.public_bytes(Encoding.Raw, PublicFormat.Raw)

        # HKDF — stretch shared secret into a proper 32-byte AES key
        aes_key = derive(shared_secret, my_pub_raw, their_pub_raw)

        # saving that contact session keys in case i talked to them again
        self._session_keys[contact] = aes_key
        print(f"[Session] Session key ready for '{contact}'")


    async def connect(self) -> None:
        pass

    async def disconnect(self) -> None:
        pass

    async def send(self, to_user: str, plaintext: str) -> None:
        pass

    def on_message(self, callback: Callable[[str, str], None]) -> None:
        pass

    async def listen(self) -> None:
        pass

    def get_history(self, contact: str) -> list[dict]:
        pass

    def _auth_headers(self) -> dict:
        if not self.token:
            raise RuntimeError("not authorized")

        return {"Authorization": f"Bearer {self.token}"}

    def _raise(self, resp: httpx.Response) -> None:
        pass

    # context manager — lets you use: async with Session() as s:
    async def __aenter__(self):
        return self

    async def __aexit__(self, *_):
        await self.disconnect()