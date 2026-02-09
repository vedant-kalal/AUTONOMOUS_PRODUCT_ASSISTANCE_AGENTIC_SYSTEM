from langchain_core.prompts import ChatPromptTemplate

def validator_prompt():
    VALIDATOR_PROMPT = ChatPromptTemplate.from_template("""
Validate the extracted intent.

Rules:
- If `product_category` is present:
    - If in {allowed} -> VALID.
    - If NOT in {allowed} -> VALID (web search).
- If `product_category` is NULL:
    - If `product_type` IS present (e.g. "laptop") -> VALID (web search). Do NOT ask for category.
    - If `product_type` is ALSO missing -> INVALID (ask for specific product).
- If `max_price` is NULL, add "budget" to missing_info list (unless query implies "any price").
- Price must be a number or null.

Intent:
{intent}

Return JSON:
{{ "validated": true | false, "missing_info": [string], "reason": "brief explanation" }}
""")
    return VALIDATOR_PROMPT
