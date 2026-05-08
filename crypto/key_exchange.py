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


