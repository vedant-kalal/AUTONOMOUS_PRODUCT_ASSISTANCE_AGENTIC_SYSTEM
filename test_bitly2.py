import os
import requests
from dotenv import load_dotenv

load_dotenv()
token = os.environ.get("BITLY_ACCESS_TOKEN", "").strip()

long_url = "https://www.google.com/search?q=trust+cart+ai+testing+long+url"

resp = requests.post(
    "https://api-ssl.bitly.com/v4/shorten",
    headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    },
    json={"long_url": long_url},
    timeout=5,
)

print(f"Status Code: {resp.status_code}")
print(f"Response: {resp.text}")
