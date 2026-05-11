from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF


#this is to take the secret key and scramble it more (removes the mathematical structure)
#and added the 2 public keys of mine and the other user since am not importing them
def derive(shared_key: bytes, my_pub_raw: bytes, their_pub_raw: bytes) -> bytes:
    salt = min(my_pub_raw, their_pub_raw) + max(my_pub_raw, their_pub_raw)
    return HKDF(
        algorithm=hashes.SHA256(),
        length=32,# it can stretch to the length i want 
        salt = salt,  # or shared transcript hash
        info=b'handshake data',
    ).derive(shared_key)