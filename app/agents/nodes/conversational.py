from app.core.config.llm_provider import load_llm
from app.core.prompt.conversational_prompt import conversational_prompt
from app.memory.memory_store import Memory_Functions
from app.tools.system_tools import Tools
from app.core.logging.utils import log_node_execution

llm = load_llm()
tools = Tools()
web_search = tools.web_search

CONVERSATION_PROMPT = conversational_prompt()


def conversational_node(state, config):
    """Simple chatbot with context awareness and web search capability"""
    
    query = state["user_query"]
    
    # Get thread_id from config for memory isolation
    thread_id = config.get("configurable", {}).get("thread_id", "default")
    
    # Get conversation summary (thread-specific)
    summary_data = Memory_Functions.get_summary(thread_id)
    summary = f"**Conversation Summary:**\n{summary_data}\n\n" if summary_data else ""
    
    # Get recent conversation history (thread-specific)
    recent_messages = Memory_Functions.get_recent_messages(thread_id)
    history = "\n".join([f"{m.type}: {m.content}" 
                        for m in recent_messages[-6:]]) if recent_messages else "No recent conversation"
    
    # Get LTM product context + user preferences (thread-specific)
    # Fetch last 5 items to allow recall of previous products (TV, etc.)
    ltm_items = Memory_Functions.get_long_term_memory(limit=5, thread_id=thread_id)
    ltm_context = ""
    
    if ltm_items:
        # Reverse to show latest first
        ltm_items.reverse()
        
        for i, product_data in enumerate(ltm_items):
            products = product_data.get("products", [])
            user_intent = product_data.get("user_intent", {})
            user_preferences = product_data.get("user_preferences", {})
            
            if products:
                import json
                product = products[0]
                title = product.get("title", "Unknown Product")
                category = product.get("category", "Unknown Category")
                price = product.get("price", "N/A")
                
                if i == 0:
                    # Detailed view for the MOST RECENT product
                    product_json = json.dumps(product, indent=2)
                    ltm_context += f"\n**Most Recent Product ({title}):**\n{product_json}\n"
                    
                    recommendation_text = product_data.get("recommendation_text", "")
                    if recommendation_text:
                        ltm_context += f"\n**Full Recommendation:**\n{recommendation_text}\n"
                    
                    if user_intent or user_preferences:
                        ltm_context += f"\n**User's Search Criteria:**\n"
                        if user_intent:
                            ltm_context += f"- Product Type: {user_intent.get('product_type', 'N/A')}\n"
                            if user_intent.get('max_price'):
                                ltm_context += f"- Budget: {user_intent.get('max_price')}\n"
                        if user_preferences:
                            for key, value in user_preferences.items():
                                ltm_context += f"- {key.replace('_', ' ').title()}: {value}\n"
                else:
                    # Summarized view for OLDER products
                    ltm_context += f"\n**Previous Product {i} ({title}):**\n"
                    ltm_context += f"- Category: {category}\n"
                    ltm_context += f"- Price: {price}\n"
                    if user_intent:
                         ltm_context += f"- User Wanted: {user_intent.get('product_type', 'Product')}\n"
            
            ltm_context += "\n---\n"
            
        # Log the primary (latest) product for tracing
        if ltm_items:
            latest = ltm_items[0].get("products", [{}])[0]
            log_node_execution(thread_id, "Conversational", f"Primary Context: {latest.get('title', 'N/A')}")
            log_node_execution(thread_id, "Conversational", f"History Depth: {len(ltm_items)} items")
    
    # Invoke LLM with web search tool
    llm_with_tools = llm.bind_tools([web_search])
    
    response = llm_with_tools.invoke(
        CONVERSATION_PROMPT.format(
            summary=summary,
            history=history,
            ltm_context=ltm_context,
            query=query
        )
    )
    
    
    # Handle tool calls (web search)
    # Extract text content properly (Gemini may return list/dict format)
    if isinstance(response.content, list):
        # Extract text from structured response
        final_response = ""
        for item in response.content:
            if isinstance(item, dict) and 'text' in item:
                final_response += item['text']
            elif isinstance(item, str):
                final_response += item
        final_response = final_response.strip()
    else:
        final_response = str(response.content)
    
    if hasattr(response, 'tool_calls') and response.tool_calls:
        log_node_execution(thread_id, "Conversational", "Using web search for query")
        for tool_call in response.tool_calls:
            if tool_call['name'] == 'web_search':
                search_results = web_search.invoke(tool_call['args'])
                
                # Re-invoke LLM with search results
                search_response = llm.invoke(
                    f"""Based on the web search results below, answer the user's question.

Web Search Results:
{search_results}

User Question: {query}

Provide a clear, helpful answer based on the search results. If the results don't contain relevant information, say so honestly.

Answer:"""
                )
                
                # Extract text from search response
                if isinstance(search_response.content, list):
                    final_response = ""
                    for item in search_response.content:
                        if isinstance(item, dict) and 'text' in item:
                            final_response += item['text']
                        elif isinstance(item, str):
                            final_response += item
                    final_response = final_response.strip()
                else:
                    final_response = str(search_response.content)
                break
    
    state["final_output"] = {
        "type": "conversation",
        "response": final_response
    }
    
    return state
