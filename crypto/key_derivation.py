from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from key_exchange import (
    key_a, key_b,
    shared_key, shared_key_2
)

derived_key = HKDF(
    algorithm = hashes.SHA256(),
    length = 32,
    salt = min(key_a,key_b) + max(key_a,key_b),
    info = b'handshake data',
).derive(shared_key)

derived_key_2 = HKDF(
    algorithm = hashes.SHA256(),
    length = 32,
    salt = min(key_a,key_b) + max(key_a,key_b),
    info = b'handshake data',
).derive(shared_key_2)

print("Derived key 1:", derived_key)
print("Derived key 2:", derived_key_2)
