import json
from encodings import utf_8
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


def _raise(resp: httpx.Response) -> None:
    resp.raise_for_status()


class Session:
    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        ws_url: str = "ws://localhost:8000",
        key_file: str = "private_key.pem"
    ):
        self.base_url = base_url
        self.ws_url = ws_url
        self.key_file = key_file
        #this is the digital identity , its in the browser you use , saved the PR
        if Path(self.key_file).exists():
            self.private_key = load_private_key(self.key_file)
            self.public_key = self.private_key.public_key()
        else:
            self.private_key, self.public_key = generate_keypair()
            # Save it to the correct path!
            save_private_key(self.private_key, path=self.key_file)

        self.username= None
        self.token = None
        self._ws  = None
        self._on_message= None
        self._session_keys={}
        self.http= httpx.Client()

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

    def _do_login(self, username: str, password: str) -> None:
        resp = self.http.post(
            f"{self.base_url}/auth/login",
            data={"username": username, "password": password}
        )
        _raise(resp)
        self.token = resp.json()["access_token"]
        self.username = username

        #  now it fetches the correct updated key and replace it
        public_hex = serialize_public_key(self.public_key)
        self.http.put(
            f"{self.base_url}/key/update",
            json={"public_key": public_hex},
            headers={"Authorization": f"Bearer {self.token}"}
        )

#contact is the person i wanna contact and talk to
    def start_chat(self, contact: str) -> bytes | None:
        #if i already have this contact before then just return the secrete key
        if contact in self._session_keys:
            return self._session_keys[contact]

        #if i don't then am get their data from header to get their public key to then create our shared secret key
        resp = self.http.get(
            f"{self.base_url}/key/{contact}",
            headers={"Authorization": f"Bearer {self.token}"}
        )


        their_pub = deserialize_public_key(resp.json()["public_key"])
        shared_secret = ecdh(self.private_key, their_pub)

        # making my public key and my contacts back to hex to derive it so its more secure
        my_pub_raw = self.public_key.public_bytes(Encoding.Raw, PublicFormat.Raw)
        their_pub_raw = their_pub.public_bytes(Encoding.Raw, PublicFormat.Raw)

        # HKDF — stretch shared secret into a proper 32-byte AES key
        aes_key = derive(shared_secret, my_pub_raw,their_pub_raw)
        # saving that contact session keys in case i talked to them again
        self._session_keys[contact] = aes_key
        return aes_key


    async def connect(self) -> None:
        uri = f"{self.ws_url}/ws/{self.username}?token={self.token}"
        self._ws = await websockets.connect(uri)

    async def disconnect(self) -> None:
        pass

    async def send(self, to_user: str, plaintext: str) -> None:
        aes_key = self.start_chat(to_user)
        ciphertext = encrypt(aes_key, plaintext.encode('utf-8'))  # returns bytes

        payload = {
            "to": to_user,
            "ciphertext": ciphertext.hex()
        }
        await self._ws.send(json.dumps(payload))

    def on_message(self, callback: Callable[[str, str], None]) -> None:
         self._on_message = callback

    async def listen(self) -> None:
         async for message in self._ws:
             data = json.loads(message)
             sender = data["from"]
             if sender not in self._session_keys:
                 self.start_chat(sender)
             aes_key = self._session_keys[sender]
             ciphertext_bytes = bytes.fromhex(data["ciphertext"])
             plaintext = decrypt(aes_key, ciphertext_bytes).decode('utf-8')
             if self._on_message:
                 self._on_message(sender, plaintext)

