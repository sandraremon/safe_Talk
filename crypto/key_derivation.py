from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from key_exchange import shared_key, shared_key_2, key_a, key_b

#this is to take the secret key and scramble it more (removes the mathematical structure)
def derive(secret: bytes) -> bytes:
    salt = min(key_a, key_b) + max(key_a, key_b)
    return HKDF(
        algorithm=hashes.SHA256(),
        length=32,# it can stretch to the length i want 
        salt = salt,  # or shared transcript hash
        info=b'handshake data',
    ).derive(secret)

derived_key = derive(shared_key) #alice derived
derived_key_2 = derive(shared_key_2) #bob derived
print("Derived key 1:", derived_key)
print("Derived key 2:", derived_key_2)