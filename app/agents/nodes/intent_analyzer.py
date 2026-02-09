from app.core.config.llm_provider import load_llm
from app.core.prompt.intent_analyzer_prompt import intent_analyzer_prompt
from app.schemas.pydantic_output_schemas.intent_schema import IntentSchema
from app.memory.memory_store import Memory_Functions
from app.core.logging.utils import log_node_execution

llm = load_llm()
INTENT_PROMPT = intent_analyzer_prompt()

def intent_analyzer_node(state, config):
    """Analyze user's purchase intent and extract product type"""
    # Get thread_id from config for memory isolation
    thread_id = config.get("configurable", {}).get("thread_id", "default")
    
    recent_messages = Memory_Functions.get_recent_messages(thread_id)
    history = "\n".join([f"{m.type}: {m.content}" for m in recent_messages[-5:]]) if recent_messages else ""

    # Use refined_query from decider if available (more context-aware)
    # Otherwise fallback to raw user_query
    query_to_analyze = state.get("refined_query", state["user_query"])
    
    # Use LangChain's native structured output with JSON mode
    structured_llm = llm.with_structured_output(IntentSchema, method='json_mode')
    result: IntentSchema = structured_llm.invoke(
        INTENT_PROMPT.format(
            query=query_to_analyze,
            history=history
        )
    )

    # Convert to dict for state
    new_intent = result.model_dump()

    # Merge with existing intent (if any) to preserve context (e.g. price)
    existing_intent = state.get("intent") or {}
    
    merged_intent = existing_intent.copy()
    for key, value in new_intent.items():
        if value is not None:
            merged_intent[key] = value

    state["intent"] = merged_intent
    return state
