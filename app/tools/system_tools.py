import os
import json
import requests
from typing import TypedDict, List, Dict, Any, Optional
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv(), override=True)

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.tools import tool

from langgraph.graph import StateGraph, END
from langchain_community.tools import DuckDuckGoSearchRun




class Tools:
    def __init__(self):
        self.url = "https://dummyjson.com/products/category"



    @tool
    def fetch_products(category: str) -> List[Dict[str, Any]]:
        """Fetch products from DummyJSON API by category."""
        url = f"https://dummyjson.com/products/category/{category}"
        res = requests.get(url)
        res.raise_for_status()
        return res.json()["products"]


    @tool
    def filter_by_price(
        products: List[Dict[str, Any]],
        max_price: Optional[float]
    ) -> List[Dict[str, Any]]:
        """Filter products by max price."""
        if max_price is None:
            return products

        return [
            p for p in products
            if isinstance(p.get("price"), (int, float)) and p["price"] <= max_price
        ]


    @tool
    def web_search(query: str) -> List[Dict[str, Any]]:
        """Search the web using Google (Serper) or fallback to DuckDuckGo."""
        try:
            # Try Google Serper first (Requires SERPER_API_KEY in .env)
            if os.environ.get("SERPER_API_KEY"):
                from langchain_community.utilities import GoogleSerperAPIWrapper
                search = GoogleSerperAPIWrapper()
                return search.run(query)
                
            # Fallback to DuckDuckGo
            search = DuckDuckGoSearchRun()
            return search.run(query)
        except Exception as e:
            return f"Search failed: {str(e)}"



