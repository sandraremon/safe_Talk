from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat, PrivateFormat, NoEncryption, load_pem_private_key
from pathlib import Path

#call this when u wanna generate a keypair for a user
def generate_keypair():
    private_key = X25519PrivateKey.generate()
    public_key  = private_key.public_key()
    return private_key, public_key

#so since the private key is the identity of the user , this save function saves your private key in a file called .pem
#.pem is in the disk of your machine , so everytime u start a session that private key will be fetched to identify you
def save_private_key(private_key, path="private_key.pem"):
    pem = private_key.private_bytes(Encoding.PEM, PrivateFormat.PKCS8, NoEncryption())
    Path(path).write_bytes(pem)

#getting the private key from .pem
def load_private_key(path="private_key.pem"):
    private_key = load_pem_private_key(Path(path).read_bytes(), password=None)
    return private_key, private_key.public_key()

#when fetching the public key and saving it it has to be in hex way so i have to serlize it after generating it
def serialize_public_key(public_key) -> str:
    return public_key.public_bytes(Encoding.Raw, PublicFormat.Raw).hex()


def deserialize_public_key(hex_str: str):
    from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PublicKey
    return X25519PublicKey.from_public_bytes(bytes.fromhex(hex_str))

#ecdh the algorithm that does the shared key to make sure the 2 users have the same secret key
def ecdh(my_private_key, their_public_key) -> bytes:
    return my_private_key.exchange(their_public_key)