from langchain_core.prompts import ChatPromptTemplate

def filter_prompt():
    FILTER_PROMPT = ChatPromptTemplate.from_template("""
You are a product filter.

User's Original Request: {original_query}
Collected Details: {collected_info}

All Products Retrieved:
{products}

Task: Filter and return ONLY products that match the user's specific request.
- Example: If user wants "red lipstick", filter out non-red items
- If no products match, return empty list

Return as JSON:
{{
  "matching_products": [list of matching product objects],
  "has_matches": true/false
}}
""")
    return FILTER_PROMPT