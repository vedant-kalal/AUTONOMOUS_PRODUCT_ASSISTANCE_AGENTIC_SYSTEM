from langchain_core.prompts import ChatPromptTemplate

def web_extract_prompt():
    WEB_EXTRACT_PROMPT = ChatPromptTemplate.from_template("""
Extract product information from the following web search results and return ONLY valid JSON.

**CRITICAL RULES:**
1. Return ONLY a JSON object - no explanations, no questions, no conversational text
2. The JSON must have a "products" array
3. If you find ANY PHYSICAL PRODUCT mention, extract it
4. EXCLUDE TV series, movies, shows, episodes, reviews, blog posts, and informational articles
5. If results are for entertainment media (e.g. "Game of Thrones"), DO NOT extract them as products
6. If results are poor or unclear, return an empty products array
7. NEVER return empty text or ask for more information

**Required JSON Format:**
{{
  "products": [
    {{
      "title": "product name",
      "price": 99.99,
      "description": "brief description",
      "category": "category if known",
      "brand": "brand if known", 
      "url": "link if available"
    }}
  ]
}}

**Search Results:**
{search_results}

Return ONLY the JSON object with the products array.
""")
    return WEB_EXTRACT_PROMPT
