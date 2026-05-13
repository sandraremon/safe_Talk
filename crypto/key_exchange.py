from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat, PrivateFormat, NoEncryption, load_pem_private_key
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PublicKey


def generate_keypair():
    private_key = X25519PrivateKey.generate()
    public_key  = private_key.public_key()
    return private_key, public_key

def save_private_key(private_key, path="private_key.pem"):
    pem = private_key.private_bytes(Encoding.Raw, PrivateFormat.Raw, NoEncryption())
    Path(path).write_bytes(pem)

def load_private_key(path="private_key.pem"):
    raw_bytes = Path(path).read_bytes()
    private_key = X25519PrivateKey.from_private_bytes(raw_bytes)
    return private_key, private_key.public_key()

def serialize_public_key(public_key) -> str:
    return public_key.public_bytes(Encoding.Raw, PublicFormat.Raw).hex()


def deserialize_public_key(hex_str: str):
    return X25519PublicKey.from_public_bytes(bytes.fromhex(hex_str))

def ecdh(my_private_key, their_public_key) -> bytes:
    return my_private_key.exchange(their_public_key)



