import os
# import your modules here
from encryption import encrypt, decrypt
from key_store import (
    alice_private_key, alice_public_key,
    bob_private_key, bob_public_key,
    derived_key, derived_key_2
)

def test_key_exchange():
    assert derived_key == derived_key_2
    print("✓ Key exchange produces identical keys")

def test_encrypt_decrypt():
    original = b"Hello, Bob!"
    encrypted = encrypt(derived_key, original)
    decrypted = decrypt(derived_key, encrypted)
    assert decrypted == original
    print("✓ Encrypt/decrypt round-trip OK")

def test_wrong_key_rejected():
    original = b"Hello, Bob!"
    encrypted = encrypt(derived_key, original)
    wrong_key = os.urandom(32)
    try:
        decrypt(wrong_key, encrypted)
        assert False, "Should have raised ValueError"
    except ValueError:
        pass
    print("✓ Wrong key correctly rejected")

def test_tampered_message_rejected():
    original = b"Hello, Bob!"
    encrypted = encrypt(derived_key, original)
    tampered = bytearray(encrypted)
    tampered[20] ^= 0xFF  # flip a byte
    try:
        decrypt(derived_key, bytes(tampered))
        assert False, "Should have raised ValueError"
    except ValueError:
        pass
    print("✓ Tampered ciphertext correctly rejected")

if __name__ == "__main__":
    test_key_exchange()
    test_encrypt_decrypt()
    test_wrong_key_rejected()
    test_tampered_message_rejected()
    print("\n All crypto tests passed — ready to build the server")