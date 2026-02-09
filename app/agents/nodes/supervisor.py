from app.core.config.llm_provider import load_llm
from app.memory.memory_store import Memory_Functions
from app.core.logging.utils import log_node_execution, log_error

llm = load_llm()


def supervisor_node(state, config):
    """Route to next step in agentic workflow"""
    
    thread_id = config.get("configurable", {}).get("thread_id", "default")
    
    try:
        # If we have final output, end
        if state.get("final_output"):
            log_node_execution(thread_id, "Supervisor", "Final output found → ending workflow")
            return {"supervisor_decision": "end"}
        
        # CRITICAL: For NEW product searches, ALWAYS ask questions
        collected_info = state.get("collected_info", {})
        
        if not collected_info or len(collected_info) == 0:
            # No questions asked yet → must collect info first
            log_node_execution(thread_id, "Supervisor", "New product search → routing to info_collector")
            return {"supervisor_decision": "need_info"}
        
        # If we have collected info, proceed to validation/retrieval
        log_node_execution(thread_id, "Supervisor", "Info collected → proceeding to query refinement")
        return {"supervisor_decision": "ready"}
        
    except Exception as e:
        log_error(thread_id, "Supervisor Node", e)
        raise
