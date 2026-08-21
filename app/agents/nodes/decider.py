from typing import Literal
from langchain_core.prompts import ChatPromptTemplate

from app.core.config.llm_provider import load_llm
from app.core.prompt.decider_prompt import decider_prompt
from app.memory.memory_store import Memory_Functions
from app.schemas.pydantic_output_schemas.decider_schema import DeciderSchema
from app.core.logging.utils import log_decision, log_node_execution

llm = load_llm()
DECIDER_PROMPT = decider_prompt()


def decider_node(state, config):
    """Route between agentic and conversational mode"""
    
    thread_id = config.get("configurable", {}).get("thread_id", "default")
    
    # Debug: Log state keys to understand why user_query might be missing
    log_node_execution(thread_id, "Decider", f"State keys: {list(state.keys())}")
    
    query = state.get("user_query")
    if not query:
        # Fallback: Try to find query in other places or history
        hist = Memory_Functions.get_recent_messages(thread_id)
        if hist and isinstance(hist[-1].content, str):
            query = hist[-1].content
            log_node_execution(thread_id, "Decider", f"Recovered query from history: {query}")
            state["user_query"] = query
        else:
            raise KeyError("user_query not found in state and could not be recovered from history")
    
    try:
        log_node_execution(thread_id, "Decider", f"Processing query: {query}")
        
        # Get conversation history (thread-specific), excluding the very last message 
        # since it is the user's CURRENT query (already saved to STM before the graph runs).
        recent_messages = Memory_Functions.get_recent_messages(thread_id)
        # Exclude the last message
        history_msgs = recent_messages[:-1] if recent_messages else []
        history = "\n".join([f"{m.type}: {m.content}" 
                            for m in history_msgs[-5:]]) if history_msgs else "No recent conversation"
        
        # Get conversation summary (thread-specific)
        summary_data = Memory_Functions.get_summary(thread_id)
        summary = ""
        if summary_data:
            summary = f"**Conversation Summary:**\n{summary_data}\n\n"
        
        # Get LTM product context (thread-specific)
        ltm = Memory_Functions.get_long_term_memory(limit=1, thread_id=thread_id)
        ltm_product_context = ""
        
        if ltm:
            product_data = ltm[0]
            products = product_data.get("products", [])
            if products:
                product_name = products[0].get("title", "")
                product_type = products[0].get("category", "")
                ltm_product_context = f"\n**Last Recommended Product:**\n- Name: {product_name}\n- Type: {product_type}\n"
        
        # Use LangChain's native structured output with JSON mode
        structured_llm = llm.with_structured_output(DeciderSchema, method='json_mode')
        result: DeciderSchema = structured_llm.invoke(
            DECIDER_PROMPT.format(
                summary=summary,
                history=history,
                ltm_context=ltm_product_context,
                query=query
            )
        )
        
        mode = result.mode
        reasoning = result.reasoning
        refined_query = result.refined_query
        
        # Log decision
        log_decision(thread_id, query, mode, reasoning)
        log_node_execution(thread_id, "Decider", f"Refined query: {refined_query}")
        
        state["mode"] = mode
        state["refined_query"] = refined_query
        
        return state
    except Exception as e:
        from app.core.logging.utils import log_error
        
        # Fallback for safety refusals (Groq 400 Error) or JSON errors
        error_msg = str(e).lower()
        if "badrequest" in error_msg or "400" in error_msg or "json" in error_msg:
             log_error(thread_id, "Decider Node Safety Fallback", e)
             # Default to conversation mode so the generic bot can handle the refusal politely
             state["mode"] = "conversation"
             state["refined_query"] = query 
             # Log the fallback
             log_decision(thread_id, query, "conversation", "Safety Fallback triggered due to LLM refusal")
             return state
            
        log_error(thread_id, "Decider Node", e)
        raise