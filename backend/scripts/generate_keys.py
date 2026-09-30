#!/usr/bin/env python3
"""
Generate Ed25519 key pair for license signing.
Run this once during initial setup.
"""
import os

import nacl.signing


def generate_keys():
    """Generate Ed25519 signing and verification key pair."""
    print("Generating Ed25519 key pair...")

    # Generate key pair
    signing_key = nacl.signing.SigningKey.generate()
    verify_key = signing_key.verify_key

    # Save private key (for license server only!)
    private_key_hex = signing_key.encode().hex()
    with open("dev_private_key.hex", "w") as f:
        f.write(private_key_hex)
    os.chmod("dev_private_key.hex", 0o600)

    # Save public key (for backend)
    public_key_hex = verify_key.encode().hex()
    with open("dev_public_key.hex", "w") as f:
        f.write(public_key_hex)

    print("\n[OK] Keys generated successfully!")
    print("\n[Public Key] (add to CLOUD_PUBLIC_KEY in config.py):")
    print(f"   {public_key_hex}")
    print("\n[Private Key] (keep secure!):")
    print(f"   {private_key_hex}")
    print("\n[Files created:]")
    print("   - dev_public_key.hex (for backend)")
    print("   - dev_private_key.hex (for license signing - KEEP SECURE!)")

    return public_key_hex, private_key_hex

if __name__ == "__main__":
    generate_keys()