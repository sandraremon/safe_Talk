from Crypto.Cipher import AES
import os

def encrypt(key, plaintext: bytes) -> bytes:
    nonce = os.urandom(12)
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    ciphertext, tag = cipher.encrypt_and_digest(plaintext)
    return nonce + ciphertext + tag


def decrypt(key, data: bytes) -> bytes:
    nonce = data[:12]
    ciphertext = data[12:-16]
    tag = data[-16:]

    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    try:
        return cipher.decrypt_and_verify(ciphertext, tag)
    except ValueError:
        raise ValueError("Message authentication failed — key wrong or data tampered")


if __name__ == "__main__":
    key = os.urandom(32)
    msg = b"Hello Bob"

    encrypted = encrypt(key, msg)
    decrypted = decrypt(key, encrypted)

    assert decrypted == msg, "Round-trip failed"
    print("Round-trip OK:", decrypted)