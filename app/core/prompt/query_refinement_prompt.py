from langchain_core.prompts import ChatPromptTemplate

def query_refinement_prompt():
    QUERY_REFINEMENT_PROMPT = ChatPromptTemplate.from_template("""
You are a query refinement specialist.

Original query: {original_query}
Product type from intent: {product_type}
Collected user preferences: {collected_info}

Create a refined, specific search query that includes:
1. The product type
2. Key specifications from collected_info (brand, color, size, budget, use case, etc.)
3. Make it concise and search-engine friendly

Examples:
- Original: "I want shoes" + collected: {{"brand": "nike", "size": "8", "use": "running"}}
  Refined: "Nike running shoes size 8"

- Original: "find me a TV" + collected: {{"brand": "sony", "size": "55 inch", "resolution": "4k"}}
  Refined: "Sony 55 inch 4K TV"

- Original: "lipstick please" + collected: {{"brand": "mac", "color": "red", "finish": "matte"}}
  Refined: "MAC red matte lipstick"

Return JSON:
{{
  "refined_query": "your refined query here"
}}
""")
    return QUERY_REFINEMENT_PROMPT