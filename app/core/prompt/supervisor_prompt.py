from langchain_core.prompts import ChatPromptTemplate

def supervisor_prompt():
    SUPERVISOR_PROMPT = ChatPromptTemplate.from_template("""
You are a workflow supervisor who decides what to do next.

Intent: {intent}
Mode: {mode}
Raw data present: {raw_data}

Return JSON:
{{ "next": "<step>" }}
""")
    return SUPERVISOR_PROMPT
