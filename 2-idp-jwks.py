#!/usr/bin/env python
import sys
from pathlib import Path
from authlib.jose import JsonWebKey, KeySet

if len(sys.argv) != 2:
    print(f"Usage: {sys.argv[0]} <key_name>")
    sys.exit(1)

key_name = sys.argv[1]

pubkey = Path(f"{key_name}_public.pem").read_text(encoding="utf-8")
jwk = JsonWebKey.import_key(pubkey, {"use": "sig", "alg": "RS256"})
print(KeySet([jwk]).as_json())