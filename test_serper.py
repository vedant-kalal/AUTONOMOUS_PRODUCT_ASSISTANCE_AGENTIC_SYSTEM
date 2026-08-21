import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()
api_key = os.environ.get("SERPER_API_KEY")

url = "https://google.serper.dev/shopping"
payload = json.dumps({"q": "best nike running shoes"})
headers = {
  'X-API-KEY': api_key,
  'Content-Type': 'application/json'
}
response = requests.post(url, headers=headers, data=payload)
print(json.dumps(response.json())[:1000])
