"""Check the OpenF1 source used by explore.py."""

import requests

response = requests.get(
    "https://api.openf1.org/v1/sessions",
    params={"year": 2024, "country_name": "Bahrain", "session_name": "Race"},
    timeout=30,
)
response.raise_for_status()
sessions = response.json()
if not sessions:
    raise SystemExit("No matching race was found.")
print("OpenF1 connection OK. Bahrain 2024 race ID:", sessions[0]["session_key"])
