#!/usr/bin/env python3
"""
Generate local license file for development.
Uses dev_private_key.hex to sign a license token.
"""
import json
import time
import nacl.signing
import os
from pathlib import Path
from app.core.security.hardware import get_machine_fingerprint

def generate_license(
    license_id: str = "DEV-LOCAL-001",
    valid_days: int = 365,
    features: list = None,
    output_path: str = None
):
    """
    Generate a signed license token for local development.

    Args:
        license_id: Unique license identifier
        valid_days: Number of days license is valid
        features: List of feature flags
        output_path: Where to save the license file
    """
    if features is None:
        features = ["full", "forecast", "sync", "bom", "purchases"]

    # Load private key
    private_key_path = "dev_private_key.hex"
    if not os.path.exists(private_key_path):
        print("[ERROR] Private key not found at {private_key_path}")
        print("   Run: python scripts/generate_keys.py first")
        return False

    with open(private_key_path, "r") as f:
        private_key_hex = f.read().strip()

    if not private_key_hex:
        print("[ERROR] Private key file is empty")
        return False

    # Create signing key
    signing_key = nacl.signing.SigningKey(bytes.fromhex(private_key_hex))

    # Get hardware fingerprint
    hardware_id = get_machine_fingerprint()
    print(f"[Hardware] Hardware ID: {hardware_id}")

    # Build license payload
    current_time = int(time.time())
    payload = {
        "license_id": license_id,
        "hardware_id": hardware_id,
        "valid_until": current_time + (valid_days * 86400),
        "issued_at": current_time,
        "features": features,
        "metadata": {
            "type": "development",
            "generated_by": "generate_license.py",
        }
    }

    # Sign payload
    payload_bytes = json.dumps(payload, separators=(',', ':')).encode('utf-8')
    signature = signing_key.sign(payload_bytes)

    # Save license file
    if output_path is None:
        license_dir = Path.home() / ".leuit"
        license_dir.mkdir(parents=True, exist_ok=True)
        output_path = license_dir / "license.key"

    license_data = {
        "token": payload_bytes.decode('utf-8'),
        "signature": signature.signature.hex(),
        "saved_at": current_time,
    }

    with open(output_path, "w") as f:
        json.dump(license_data, f, indent=2)

    print("\n[OK] License generated successfully!")
    print(f"[Saved] Saved to: {output_path}")
    print(f"\n[License Details]")
    print(f"   License ID: {license_id}")
    print(f"   Hardware ID: {hardware_id}")
    print(f"   Valid Until: {time.ctime(payload['valid_until'])} ({valid_days} days)")
    print(f"   Features: {', '.join(features)}")

    return True

def main():
    import argparse

    parser = argparse.ArgumentParser(description="Generate LEUIT license file")
    parser.add_argument("--id", default="DEV-LOCAL-001", help="License ID")
    parser.add_argument("--days", type=int, default=365, help="Validity in days")
    parser.add_argument("--output", help="Output file path")
    parser.add_argument("--features", nargs="+", default=["full"], help="Feature flags")

    args = parser.parse_args()

    print("[License] LEUIT License Generator")
    print("=" * 40)

    generate_license(
        license_id=args.id,
        valid_days=args.days,
        features=args.features,
        output_path=args.output
    )

if __name__ == "__main__":
    main()