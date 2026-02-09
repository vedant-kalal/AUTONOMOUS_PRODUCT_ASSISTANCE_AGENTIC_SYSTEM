from langchain_core.prompts import ChatPromptTemplate

def response_generator_prompt():
    RESPONSE_PROMPT = ChatPromptTemplate.from_template("""
You are a product recommendation assistant.

User Query: {user_query}
User Preference Context: {collected_info}

Given the structured product data below, generate a clear, attractive, and helpful response.

Rules:
- Summarize results relevant to the user's query
- Highlight how these options meet their specific preferences (from context)
- Mention price, key features
- Be concise and friendly

Product data:
{products}
""")
    return RESPONSE_PROMPT
