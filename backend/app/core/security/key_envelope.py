import hashlib
import secrets
import time

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from nacl.public import PrivateKey, PublicKey, SealedBox

DEK_SIZE = 32
SALT_SIZE = 16
NONCE_SIZE = 12
PBKDF2_ITERATIONS = 100_000


class KeyEnvelope:
    """
    Dual-Key Envelope Encryption for SQLCipher DEK.
    The DEK is encrypted twice:
    1. Envelope A: Encrypted with Owner's passkey (PBKDF2 derived key)
    2. Envelope B: Encrypted with Developer's Master Public Key (Sealed Box)
    """

    @staticmethod
    def generate_dek() -> bytes:
        return secrets.token_bytes(DEK_SIZE)

    @staticmethod
    def derive_owner_key(passkey: str, salt: bytes) -> bytes:
        return hashlib.pbkdf2_hmac('sha256', passkey.encode(), salt, PBKDF2_ITERATIONS, dklen=DEK_SIZE)

    @staticmethod
    def encrypt_dek_for_owner(dek: bytes, passkey: str) -> tuple[bytes, bytes]:
        """
        Encrypt DEK with Owner's passkey.
        Returns (encrypted_dek, salt).
        """
        salt = secrets.token_bytes(SALT_SIZE)
        owner_key = KeyEnvelope.derive_owner_key(passkey, salt)

        # Use AES-GCM for authenticated encryption
        aesgcm = AESGCM(owner_key)
        nonce = secrets.token_bytes(NONCE_SIZE)
        encrypted = aesgcm.encrypt(nonce, dek, None)

        # Store salt + nonce + ciphertext together
        return salt + nonce + encrypted, salt

    @staticmethod
    def decrypt_dek_for_owner(encrypted_package: bytes, passkey: str) -> bytes:
        """
        Decrypt DEK using Owner's passkey.
        encrypted_package format: salt (16) + nonce (12) + ciphertext
        """
        if len(encrypted_package) < SALT_SIZE + NONCE_SIZE:
            raise ValueError("Invalid encrypted package format")

        salt = encrypted_package[:SALT_SIZE]
        nonce = encrypted_package[SALT_SIZE:SALT_SIZE + NONCE_SIZE]
        ciphertext = encrypted_package[SALT_SIZE + NONCE_SIZE:]

        owner_key = KeyEnvelope.derive_owner_key(passkey, salt)
        aesgcm = AESGCM(owner_key)

        try:
            dek = aesgcm.decrypt(nonce, ciphertext, None)
            return dek
        except Exception:
            raise ValueError("Invalid passkey or corrupted data")

    @staticmethod
    def encrypt_dek_for_developer(dek: bytes, dev_public_key: PublicKey) -> bytes:
        """
        Encrypt DEK with Developer's Master Public Key using Sealed Box (anonymous encryption).
        Returns encrypted DEK package.
        """
        sealed_box = SealedBox(dev_public_key)
        return sealed_box.encrypt(dek)

    @staticmethod
    def decrypt_dek_for_developer(encrypted_package: bytes, dev_private_key: PrivateKey) -> bytes:
        """
        Decrypt DEK using Developer's Master Private Key.
        """
        sealed_box = SealedBox(dev_private_key)
        try:
            return sealed_box.decrypt(encrypted_package)
        except Exception as exc:
            raise ValueError("Invalid developer key or corrupted data") from exc

    @staticmethod
    def create_envelope(dek: bytes, owner_passkey: str, dev_public_key: PublicKey) -> dict:
        """
        Create dual-key envelope for DEK.
        Returns dict with both encrypted envelopes.
        """
        # Encrypt for Owner
        owner_encrypted, salt = KeyEnvelope.encrypt_dek_for_owner(dek, owner_passkey)

        # Encrypt for Developer
        dev_encrypted = KeyEnvelope.encrypt_dek_for_developer(dek, dev_public_key)

        return {
            "encrypted_dek_owner": owner_encrypted.hex(),
            "encrypted_dek_developer": dev_encrypted.hex(),
            "salt": salt.hex(),
            "version": 1,
            "created_at": int(time.time()),
        }

    @staticmethod
    def open_envelope_owner(envelope: dict, owner_passkey: str) -> bytes:
        """Open envelope using Owner's passkey."""
        encrypted_package = bytes.fromhex(envelope["encrypted_dek_owner"])
        return KeyEnvelope.decrypt_dek_for_owner(encrypted_package, owner_passkey)

    @staticmethod
    def open_envelope_developer(envelope: dict, dev_private_key: PrivateKey) -> bytes:
        """Open envelope using Developer's private key."""
        encrypted_package = bytes.fromhex(envelope["encrypted_dek_developer"])
        return KeyEnvelope.decrypt_dek_for_developer(encrypted_package, dev_private_key)


# SQLCipher-specific key derivation
def derive_sqlcipher_key(dek: bytes, iterations: int = 256000) -> str:
    """
    Derive SQLCipher-compatible key from DEK.
    SQLCipher uses PBKDF2-HMAC-SHA256 with specified iterations.
    """

    # SQLCipher expects the key as hex string
    # We use the DEK directly as the raw key material
    return dek.hex()


def generate_key_rotation_package(
    old_dek: bytes,
    new_owner_passkey: str,
    dev_public_key: PublicKey
) -> dict:
    """Generate new envelope for key rotation."""
    new_dek = KeyEnvelope.generate_dek()
    new_envelope = KeyEnvelope.create_envelope(new_dek, new_owner_passkey, dev_public_key)

    return {
        "new_dek": new_dek.hex(),
        "new_envelope": new_envelope,
        "old_dek_hash": hashlib.sha256(old_dek).hexdigest(),
        "rotated_at": int(time.time()),
    }