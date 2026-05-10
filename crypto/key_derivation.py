from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from key_exchange import (
    shared_key, shared_key_2
)

import os
from cryptography.hazmat.primitives import hashes

def derive(shared_key):
    return HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=os.urandom(16),  # or shared transcript hash
        info=b'handshake data',
    ).derive(shared_key)

derived_key = derive(shared_key)
derived_key_2 = derive(shared_key_2)

print("Derived key 1:", derived_key)
print("Derived key 2:", derived_key_2)
