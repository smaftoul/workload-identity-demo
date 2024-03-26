#!/usr/bin/env python
import os
import sys
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa


def generate_rsa_key_pem(file_prefix, key_size=2048):
    try:
        os.makedirs(os.path.dirname(file_prefix))
        print(f"Directory '{os.path.dirname(file_prefix)}' created")
    except OSError:
        pass

    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=key_size,
    )

    with open(f"{file_prefix}_private.pem", "wb") as f:
        f.write(
            private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption(),
            )
        )

    with open(f"{file_prefix}_public.pem", "wb") as f:
        f.write(
            private_key.public_key().public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo,
            )
        )


if len(sys.argv) != 2:
    print(f"Usage: {sys.argv[0]} <key_name>")
    sys.exit(1)

key_name = sys.argv[1]

try:
    with open(f"{key_name}_private.pem", "r") as f:
        print(f"Key file {key_name}_private.pem already exists, skipping")
except FileNotFoundError:
    generate_rsa_key_pem(key_name)
    print(f"Key file {key_name}_private.pem and {key_name}_public.pem created")
