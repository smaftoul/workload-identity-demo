#!/usr/bin/env python
import datetime
import sys
import requests
from pathlib import Path
from authlib.jose import jwt
from opentelemetry_resourcedetector_process import ProcessResourceDetector

if len(sys.argv) != 2:
    print(f"Usage: {sys.argv[0]} <key_name>")
    sys.exit(1)

key_name = sys.argv[1]

process_info = ProcessResourceDetector().detect().attributes.__dict__
# _lock is not serializable
process_info.__delitem__("_lock")

claim = {
    "aud": ["audience"],
    "iss": "https://some-address",
    "sub": "some-workload",
    "exp": int(
        (
            datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(days=1)
        ).timestamp()
    ),
    "iat": int(datetime.datetime.now(tz=datetime.timezone.utc).timestamp()),
    "otel": process_info,
    "weather": {
        "paris": requests.get("http://wttr.in/Paris?format=j1").json()[
            "current_condition"
        ][0]["weatherDesc"][0]["value"],
    },
}

key_data = Path(f"{key_name}_private.pem").read_text(encoding="utf-8")
print(jwt.encode(header={"alg": "RS256"}, payload=claim, key=key_data).decode("utf-8"))
