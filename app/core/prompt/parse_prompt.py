from langchain_core.prompts import ChatPromptTemplate

def parse_prompt():

    PARSE_PROMPT = ChatPromptTemplate.from_template("""
    You are a STRICT product intent parser.

    Allowed categories ONLY:
    - beauty
    - groceries
    - fragrances
    - furniture

    Rules:
    - If product does NOT belong to these categories, return EMPTY JSON.
    - Do NOT guess.
    - If budget missing → max_price = null.
    - Return ONLY JSON.

    Valid:
    {{
    "category": "beauty",
    "max_price": 20
    }}

    Invalid:
    {{}}

    User query:
    {query}
    """)
    return PARSE_PROMPT
