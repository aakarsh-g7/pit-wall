import fastf1
import requests

race = fastf1.get_session(2024, "Bahrain", "R")

url = (
    "https://livetiming.formula1.com"
    + race.api_path
    + "SessionInfo.jsonStream"
)

response = requests.get(
    url,
    headers={"User-Agent": "BestHTTP"},
    timeout=20
)

print("URL:", url)
print("Status:", response.status_code)
print("Response:", response.text[:200])