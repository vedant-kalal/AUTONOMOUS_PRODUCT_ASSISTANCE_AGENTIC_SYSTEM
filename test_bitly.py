import os
import sys

# Ensure app is in path
sys.path.append("/home/vedant/Desktop/Personal-Projects/Trust_Cart_AI/AUTONOMOUS_PRODUCT_ASSISTANCE_AGENTIC_SYSTEM")

from dotenv import load_dotenv
from app.tools.url_shortener import shorten_url

load_dotenv()

token = os.environ.get("BITLY_ACCESS_TOKEN")
print(f"Testing Bitly API...")
print(f"Token found: {token[:4]}...{token[-4:]}" if token else "No token found!")

test_url = "https://www.google.com/search?q=trust+cart+ai+testing+long+url"
print(f"Original URL: {test_url}")

try:
    short_url = shorten_url(test_url)
    print(f"Shortened URL: {short_url}")
    if "bit.ly" in short_url:
        print("✅ SUCCESS! Bitly API is working perfectly.")
    elif short_url == test_url:
        print("❌ FAILED: API returned the original URL. Check if the token is valid.")
    else:
        print(f"⚠️ UNEXPECTED: {short_url}")
except Exception as e:
    print(f"❌ ERROR: {e}")
