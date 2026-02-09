from app.memory.memory_store import Memory_Functions
from app.core.logging.utils import log_memory_operation


def memory_store_node(state, config):
    """Store products, user preferences in LTM; override old recommendations"""
    thread_id = config.get("configurable", {}).get("thread_id", "default")
    
    collected_info = state.get("collected_info", {})
    # Prioritize final_output products (what was shown to user) over raw_data
    products = []
    if state.get("final_output"):
        products = state["final_output"].get("products", [])
    
    if not products:
        products = state.get("raw_data", [])
        
    source = collected_info.get("source", "unknown")
    
    # Old logic wiped LTM every turn. We want to append history now.
    # Removed: Memory_Functions.clear_long_term_memory(thread_id)
    
    # Store new products with user preferences
    user_prefs = {
        k: v for k, v in collected_info.items() 
        if k not in ["products", "source", "refined_query"]
    }
    
    try:
        # Prepare data dictionary
        memory_data = {
            "products": products,
            "user_preferences": user_prefs,
            "user_intent": state.get("intent", {}),
            "stored_at_step": "memory_store_node"
        }
        
        Memory_Functions.store_long_term_memory(
            data=memory_data,
            thread_id=thread_id
        )
        
        product_count = len(products)
        log_memory_operation(
            thread_id,
            "LTM Stored",
            f"{product_count} product(s) stored | Preferences: {list(user_prefs.keys())}"
        )
    except Exception as e:
        log_memory_operation(thread_id, "LTM Store Failed", str(e))
    
    return state