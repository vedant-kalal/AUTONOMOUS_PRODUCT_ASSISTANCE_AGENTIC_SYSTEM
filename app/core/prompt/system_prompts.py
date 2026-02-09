from langchain_core.prompts import ChatPromptTemplate

def intent_analyzer_prompt():
    INTENT_ANALYZER_PROMPT = ChatPromptTemplate.from_template("""
You are an intent analyzer for a product recommendation system.

Your task is to extract structured information from the user's query.

**Extract the following fields:**
- `product_type`: The specific product the user wants (e.g., "lipstick", "shoes", "laptop", "tv", "sofa") - **ALWAYS extract this if mentioned**
- `product_category`: One of the allowed categories below, or null if product doesn't fit
- `max_price`: The maximum price mentioned, or null

**Allowed Categories (optional):**
- beauty (examples: lipstick, mascara, foundation)
- groceries (examples: apple, milk, bread, vegetables)
- fragrances (examples: cologne, perfume, scent)
- furniture (examples: sofa, chair, table, bed)

**IMPORTANT RULES:**
1. **ALWAYS extract product_type** from phrases like:
   - "find me X"
   - "I want X"
   - "looking for X"
   - "X recommendation"
   - "a new X"
   - "show me X"

2. **product_category is OPTIONAL** - Only set if product_type clearly fits one of the 4 allowed categories
   - If product doesn't fit (e.g., TV, laptop, phone), set product_category to null
   - The system can still search for these products!

3. Extract max_price from phrases like "under $X", "$X budget", "max $X"

**Examples:**

Query: "find me a lipstick"
{{
  "product_type": "lipstick",
  "product_category": "beauty",
  "max_price": null
}}

Query: "I want running shoes under $100"
{{
  "product_type": "running shoes",
  "product_category": null,
  "max_price": 100.0
}}

Query: "find me a new tv"
{{
  "product_type": "tv",
  "product_category": null,
  "max_price": null
}}

Query: "show me a sofa with budget 5000 rupees"
{{
  "product_type": "sofa",
  "product_category": "furniture",
  "max_price": 5000.0
}}

Query: "find me mascara"
{{
  "product_type": "mascara",
  "product_category": "beauty",
  "max_price": null
}}

User query:
{query}

Recent Conversation Context (for additional clues):
{history}

Return ONLY valid JSON with these exact fields: product_type, product_category, max_price
""")
    return INTENT_ANALYZER_PROMPT

def supervisor_prompt():
    SUPERVISOR_PROMPT = ChatPromptTemplate.from_template("""
You are the supervisor of an AI agent.

Decide the NEXT STEP.

Possible steps:
- "collect_info"
- "validate"
- "retrieve_data"
- "reason"
- "store_memory"
- "end"

State:
Intent: {intent}
Missing info: {missing}
Validated: {validated}
Raw data present: {raw_data}

Return JSON:
{{ "next": "<step>" }}
""")
    return SUPERVISOR_PROMPT

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

def web_extract_prompt():
    WEB_EXTRACT_PROMPT = ChatPromptTemplate.from_template("""
Extract product information from the following web search results and return ONLY valid JSON.

**CRITICAL RULES:**
1. Return ONLY a JSON object - no explanations, no questions, no conversational text
2. The JSON must have a "products" array
3. If you find ANY product mention, extract it
4. If results are poor or unclear, create a generic product entry based on the query context
5. NEVER return empty text or ask for more information

**Required JSON Format:**
{{
  "products": [
    {{
      "title": "Product Name",
      "price": 99.99,
      "description": "Brief description"
    }}
  ]
}}

**Example:**
Search: "Sony 55 inch 4K TV for $499"
Output:
{{
  "products": [
    {{
      "title": "Sony 55-inch 4K TV",
      "price": 499,
      "description": "Sony 4K television"
    }}
  ]
}}

**Web Search Results:**
{search_results}

**Your response (JSON ONLY, no other text):**
""")
    return WEB_EXTRACT_PROMPT


def decider_prompt():
    DECIDER_PROMPT = ChatPromptTemplate.from_template("""
You are an intelligent conversation router that decides whether to search for a NEW product or answer questions about EXISTING products.

{summary}

**Recent Conversation:**
{history}

**Long Term Memory (LTM) Context:**
{ltm_context}

**User's Current Query:**
{query}

---

**Your Task:**
Analyze the query and decide: Is this a NEW product search OR a follow-up question about an existing product?

**🔍 Detection Rules (Priority Order):**

1. **Route to "conversation" if ANY of these are true:**
   - Query asks about **attributes of a product mentioned in history/LTM**
     - Attribute keywords: price, cost, name, title, brand, color, shade, size, specification, feature, detail, availability, stock, review, rating, warranty, shipping
     - Examples:
       * History has "Creed perfume" → "find me price of creed" → **conversation** (asking about price of EXISTING product)
       * History has "Nike shoes" → "what is the name?" → **conversation**
       * History has "Sony TV" → "show me reviews" → **conversation**
   
   - Query mentions **same product type/brand as in LTM**
     - Examples:
       * LTM has "Creed perfume" → "find me expensive creed perfumes" → **conversation** (still about Creed)
       * LTM has "Nike shoes" → "find me other nike colors" → **conversation** (still about Nike)
   
   - Query is **general chit-chat**
     - Examples: "hi", "thanks", "great", "okay", "yes", "no"

2. **Route to "agentic" ONLY if:**
   - User explicitly wants a **COMPLETELY DIFFERENT product type**
     - Examples:
       * History has "perfume" → "find me shoes" → **agentic** (different product!)
       * History has "TV" → "I want a laptop" → **agentic** (different product!)
   
   - Query is a **brand new search with no context**
     - Examples:
       * History empty → "find me perfume" → **agentic**

---

**⚠️ AVOID FALSE POSITIVES - Stay in "conversation" for vague queries:**
- "new", "i said new", "new one" → User wants new variant of CURRENT product
- "different", "another", "something else" → User wants alternatives to CURRENT product  
- "change", "switch" → Likely refinement of CURRENT product
- Short unclear phrases → Default to **conversation** (safer)

**Context Rules:**
- If recent history discusses SHOES and user says "i want new" → They mean new SHOES (**conversation**)
- If recent history discusses TV and user says "different color" → They mean different TV (**conversation**)
- ONLY route to agentic if new product type is EXPLICITLY stated (e.g., "find me laptop" when discussing shoes)

**Decision Logic:**
1. Check if query is vague/short → YES = **conversation** (safest assumption)
2. Check if query mentions product from LTM/history → YES = check for attributes
3. Check if query has attribute keywords → YES = **conversation**
4. Check if query EXPLICITLY wants different product type → YES = **agentic**
5. Default → **conversation** (safer to stay in context)

---

**Return JSON (REQUIRED):**
{{
  "mode": "conversation" or "agentic",
  "reasoning": "explain your decision in 1 sentence",
  "refined_query": "A clear, context-aware query that states exactly what the user wants. If mode is 'agentic', extract and clarify the product type. Examples: 'User wants to find running shoes', 'User is looking for a 4K TV under $500', 'User needs a red matte lipstick from MAC'"
}}
""")
    return DECIDER_PROMPT

def info_collector_prompt():    
    INFO_COLLECTOR_PROMPT = ChatPromptTemplate.from_template("""
You are a product assistant that asks relevant questions to help find the best product for the user.

**Product Type:** {product_type}
**Current Intent:** {intent}

**Your Task:**
Generate 3-5 specific, relevant questions to help the user find the perfect {product_type}.

**Question Guidelines by Product Type:**

- **Laptop**: budget, primary use (work/gaming/content creation), screen size preference, brand preference, RAM/storage needs, graphics card requirements
- **TV**: budget, screen size, resolution (4K/8K), primary use (streaming/gaming/sports), brand preference, smart TV features
- **Shoes**: size, type (running/casual/formal), brand preference, color preference, specific use case
- **Lipstick/Beauty**: budget, shade/color preference, finish (matte/glossy), brand preference, skin tone
- **Furniture**: budget, dimensions, style (modern/classic/rustic), color, material preference
- **Phone**: budget, screen size, brand preference, storage capacity, camera quality needs
- **Graphic Card**: budget, VRAM requirement, primary use (gaming/AI/rendering), brand (NVIDIA/AMD), power supply capacity

**Rules:**
1. Ask domain-specific questions relevant to the product type
2. Skip questions if information is already provided in intent
3. Keep questions clear, concise, and conversational
4. Generate AT LEAST 3 questions, maximum 5
5. Do NOT ask about shoe size for laptops or irrelevant questions!

**Return Format (REQUIRED JSON):**
{{
  "list_of_questions": [
    "What is your budget range?",
    "What will you primarily use the {product_type} for?",
    "Do you have any brand preferences?"
  ]
}}
""")
    return INFO_COLLECTOR_PROMPT

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

def conversational_prompt():
    CONVERSATION_PROMPT = ChatPromptTemplate.from_template("""
You are a helpful product assistant chatbot. Your goal is to answer the user's questions using the context provided.

{summary}

**Recent Conversation:**
{history}

**Long Term Memory (Product Context):**
{ltm_context}

**User's Question:**
{query}

---

**Instructions:**

1. **First, check the context above** (Summary, Recent Conversation, LTM Product):
   - If the answer is in the context, provide a clear, helpful response
   - Use product details from LTM when answering about recommended products
   - Reference conversation history when relevant

2. **If context doesn't have the answer**:
   - Use the `web_search` tool to find information
   - The tool will search the web and you can use those results to answer

3. **Response Guidelines:**
   - Be conversational and friendly
   - Keep responses concise but complete
   - If you truly don't know something and can't search for it, say so honestly
   - For product attribute questions (price, name, specs), check LTM first
   - For follow-up questions, maintain conversation context

**Examples:**

User: "what is the price?"
Context: LTM has product with price $99
→ "The product is priced at $99."

User: "what colors does it come in?"
Context: No color info in LTM
→ Use web_search tool → Answer based on results

User: "thanks!"
→ "You're welcome! Let me know if you need anything else."

**Your Response:**
""")
    return CONVERSATION_PROMPT

def response_generator_prompt():
    RESPONSE_PROMPT = ChatPromptTemplate.from_template("""
You are a product recommendation assistant.

Given the structured product data below,
generate a clear, attractive, and helpful response.

Rules:
- Summarize results
- Highlight best options
- Mention price, key features
- Be concise and friendly

Product data:
{data}
""")
    return RESPONSE_PROMPT
