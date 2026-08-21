import sys
sys.path.append("/home/vedant/Desktop/Personal-Projects/Trust_Cart_AI/AUTONOMOUS_PRODUCT_ASSISTANCE_AGENTIC_SYSTEM")
from app.tools.url_shortener import shorten_url
import requests

# Patch requests.post to see exactly what is passed
original_post = requests.post
def mock_post(*args, **kwargs):
    print("requests.post called with args:", args)
    print("kwargs:", kwargs)
    resp = original_post(*args, **kwargs)
    print("Status code:", resp.status_code)
    print("Response JSON:", resp.json())
    return resp
requests.post = mock_post

short_url = shorten_url("https://www.google.com/search?q=trust+cart+ai+testing+long+url")
print("Returned:", short_url)
