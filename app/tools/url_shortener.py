"""
URL Shortener Utility — Bitly API
Shortens long product URLs before passing them to the LLM context window.
Falls back to the original URL if Bitly is unavailable or not configured.
"""

import os
import requests
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


def shorten_url(long_url: str) -> str:
    """
    Shorten a URL using the Bitly API.
    Returns the original URL if shortening fails or token is missing.
    """
    if not long_url or not long_url.startswith("http"):
        return long_url

    token = os.environ.get("BITLY_ACCESS_TOKEN", "").strip()
    if not token or token == "your_bitly_token_here":
        return long_url  # No real token configured → pass through unchanged

    try:
        resp = requests.post(
            "https://api-ssl.bitly.com/v4/shorten",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
            json={"long_url": long_url},
            timeout=5,
        )
        if resp.status_code in (200, 201):
            return resp.json().get("link", long_url)
        elif resp.status_code == 422:
            # Already a short URL or invalid — return as-is
            return long_url
        else:
            return long_url
    except Exception:
        return long_url


def shorten_products_urls(products: list) -> list:
    """
    Shorten the 'url' and 'thumbnail' is NOT shortened (images need full URL).
    Only the buy/product link is shortened.
    Returns updated product list.
    """
    shortened = []
    for p in products:
        if not isinstance(p, dict):
            shortened.append(p)
            continue
        product = dict(p)  # shallow copy — don't mutate original
        if product.get("url"):
            product["url"] = shorten_url(product["url"])
        shortened.append(product)
    return shortened
