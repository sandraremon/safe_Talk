from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
# Generate a private key for use in the exchange.

alice_private_key = X25519PrivateKey.generate()
alice_public_key = alice_private_key.public_key()

bob_private_key= X25519PrivateKey.generate()
bob_public_key = bob_private_key.public_key()
shared_key = alice_private_key.exchange(bob_public_key)
key_a= alice_public_key.public_bytes(Encoding.Raw, PublicFormat.Raw)
shared_key_2 = bob_private_key.exchange(alice_public_key)
key_b= bob_public_key.public_bytes(Encoding.Raw, PublicFormat.Raw)
# Perform key derivation.
derived_key = HKDF(
    algorithm=hashes.SHA256(),
    length=32,
    salt=min(key_a,key_b)+max(key_a,key_b),
    info=b'handshake data',
).derive(shared_key)


derived_key_2 = HKDF(
    algorithm=hashes.SHA256(),
    length=32,
    salt=min(key_a,key_b)+max(key_a,key_b),
    info=b'handshake data',
).derive(shared_key_2)

print("Derived key 1:", derived_key)
print("Derived key 2:", derived_key_2)

