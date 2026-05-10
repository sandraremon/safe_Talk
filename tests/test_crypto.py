"""
tests/test_crypto.py
Tests for all three crypto modules: key_exchange, key_derivation, encryption.
Run with: pytest tests/test_crypto.py -v
"""
import os
import pytest
from pathlib import Path


# ── helpers ──────────────────────────────────────────────────────────────────

def make_peer():
    """Return a fresh (private_key, public_key) pair."""
    from crypto.key_exchange import generate_keypair
    return generate_keypair()


# ═════════════════════════════════════════════════════════════════════════════
# key_exchange
# ═════════════════════════════════════════════════════════════════════════════

class TestKeyExchange:

    def test_generate_keypair_returns_two_keys(self):
        from crypto.key_exchange import generate_keypair
        priv, pub = generate_keypair()
        assert priv is not None
        assert pub is not None

    def test_public_key_matches_private(self):
        from crypto.key_exchange import generate_keypair
        priv, pub = generate_keypair()
        assert priv.public_key().public_bytes_raw() == pub.public_bytes_raw()

    def test_save_and_load_private_key(self, tmp_path):
        """Round-trip: save → load → same raw bytes."""
        from crypto.key_exchange import generate_keypair, save_private_key, load_private_key
        from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

        priv, pub = generate_keypair()
        pem_path = str(tmp_path / "test_key.pem")
        save_private_key(priv, path=pem_path)

        # ⚠️  load_private_key returns a TUPLE (priv, pub) — unpack it
        loaded_priv, loaded_pub = load_private_key(pem_path)

        assert (
            priv.private_bytes_raw() == loaded_priv.private_bytes_raw()
        ), "Loaded private key bytes must match the original"

    def test_serialize_deserialize_public_key(self):
        from crypto.key_exchange import generate_keypair, serialize_public_key, deserialize_public_key
        _, pub = generate_keypair()

        hex_str = serialize_public_key(pub)
        assert isinstance(hex_str, str)
        assert len(hex_str) == 64          # 32 raw bytes → 64 hex chars

        recovered = deserialize_public_key(hex_str)
        assert recovered.public_bytes_raw() == pub.public_bytes_raw()

    def test_ecdh_both_sides_agree(self):
        """Alice and Bob must derive the same shared secret."""
        from crypto.key_exchange import generate_keypair, ecdh
        alice_priv, alice_pub = generate_keypair()
        bob_priv,   bob_pub   = generate_keypair()

        alice_secret = ecdh(alice_priv, bob_pub)
        bob_secret   = ecdh(bob_priv,   alice_pub)

        assert alice_secret == bob_secret

    def test_ecdh_different_peers_give_different_secrets(self):
        from crypto.key_exchange import generate_keypair, ecdh
        alice_priv, alice_pub = generate_keypair()
        bob_priv,   bob_pub   = generate_keypair()
        carol_priv, carol_pub = generate_keypair()

        secret_ab = ecdh(alice_priv, bob_pub)
        secret_ac = ecdh(alice_priv, carol_pub)

        assert secret_ab != secret_ac


# ═════════════════════════════════════════════════════════════════════════════
# key_derivation
# ═════════════════════════════════════════════════════════════════════════════

class TestKeyDerivation:

    def _raw(self, pub):
        from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
        return pub.public_bytes(Encoding.Raw, PublicFormat.Raw)

    def test_derive_returns_32_bytes(self):
        from crypto.key_derivation import derive
        shared = os.urandom(32)
        a, b = os.urandom(32), os.urandom(32)
        key = derive(shared, a, b)
        assert len(key) == 32

    def test_derive_is_deterministic(self):
        from crypto.key_derivation import derive
        shared = os.urandom(32)
        a, b = os.urandom(32), os.urandom(32)
        assert derive(shared, a, b) == derive(shared, a, b)

    def test_derive_symmetric_salt(self):
        """
        Salt is built from sorted(pub_a, pub_b), so Alice and Bob must
        get the same AES key regardless of argument order.
        """
        from crypto.key_derivation import derive
        shared = os.urandom(32)
        a, b = os.urandom(32), os.urandom(32)
        assert derive(shared, a, b) == derive(shared, b, a)

    def test_derive_different_shared_secrets(self):
        from crypto.key_derivation import derive
        a, b = os.urandom(32), os.urandom(32)
        key1 = derive(os.urandom(32), a, b)
        key2 = derive(os.urandom(32), a, b)
        assert key1 != key2

    def test_full_e2e_key_agreement(self):
        """
        Full handshake: Alice and Bob run ECDH + HKDF and must end up
        with the exact same 32-byte AES key.
        """
        from crypto.key_exchange import generate_keypair, ecdh
        from crypto.key_derivation import derive
        from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

        alice_priv, alice_pub = generate_keypair()
        bob_priv,   bob_pub   = generate_keypair()

        alice_shared = ecdh(alice_priv, bob_pub)
        bob_shared   = ecdh(bob_priv,   alice_pub)

        alice_raw = alice_pub.public_bytes(Encoding.Raw, PublicFormat.Raw)
        bob_raw   = bob_pub.public_bytes(Encoding.Raw, PublicFormat.Raw)

        alice_key = derive(alice_shared, alice_raw, bob_raw)
        bob_key   = derive(bob_shared,   alice_raw, bob_raw)

        assert alice_key == bob_key, "Both sides must derive the identical AES key"


# ═════════════════════════════════════════════════════════════════════════════
# encryption
# ═════════════════════════════════════════════════════════════════════════════

class TestEncryption:

    def _key(self):
        return os.urandom(32)

    def test_encrypt_returns_bytes(self):
        from crypto.encryption import encrypt
        ct = encrypt(self._key(), b"hello")
        assert isinstance(ct, bytes)

    def test_ciphertext_length(self):
        """nonce(12) + ciphertext(N) + tag(16)"""
        from crypto.encryption import encrypt
        plaintext = b"hello world"
        ct = encrypt(self._key(), plaintext)
        assert len(ct) == 12 + len(plaintext) + 16

    def test_round_trip(self):
        from crypto.encryption import encrypt, decrypt
        key = self._key()
        msg = b"Secret message"
        assert decrypt(key, encrypt(key, msg)) == msg

    def test_encrypt_is_random(self):
        """Two encryptions of the same plaintext must differ (random nonce)."""
        from crypto.encryption import encrypt
        key = self._key()
        msg = b"Same message"
        assert encrypt(key, msg) != encrypt(key, msg)

    def test_wrong_key_raises(self):
        from crypto.encryption import encrypt, decrypt
        ct = encrypt(self._key(), b"top secret")
        with pytest.raises(ValueError, match="authentication failed"):
            decrypt(self._key(), ct)   # different key

    def test_tampered_ciphertext_raises(self):
        from crypto.encryption import encrypt, decrypt
        key = self._key()
        ct = bytearray(encrypt(key, b"don't tamper"))
        ct[15] ^= 0xFF                 # flip a byte in the ciphertext body
        with pytest.raises(ValueError):
            decrypt(key, bytes(ct))

    def test_tampered_tag_raises(self):
        from crypto.encryption import encrypt, decrypt
        key = self._key()
        ct = bytearray(encrypt(key, b"don't tamper tag"))
        ct[-1] ^= 0xFF                 # flip last byte of the GCM tag
        with pytest.raises(ValueError):
            decrypt(key, bytes(ct))

    def test_empty_plaintext(self):
        from crypto.encryption import encrypt, decrypt
        key = self._key()
        assert decrypt(key, encrypt(key, b"")) == b""

    def test_large_plaintext(self):
        from crypto.encryption import encrypt, decrypt
        key = self._key()
        msg = os.urandom(10_000)
        assert decrypt(key, encrypt(key, msg)) == msg