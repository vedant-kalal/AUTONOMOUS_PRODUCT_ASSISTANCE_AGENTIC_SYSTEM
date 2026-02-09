from app.core.config.llm_provider import load_llm
from app.core.prompt.query_refinement_prompt import query_refinement_prompt
from app.schemas.pydantic_output_schemas.query_refinement_schema import QueryRefinementSchema
from app.core.logging.utils import log_node_execution, log_error

llm = load_llm()
PROMPT = query_refinement_prompt()


def query_refinement_node(state, config):
    """Refine search query by combining intent analysis + collected user preferences"""
    
    thread_id = config.get("configurable", {}).get("thread_id", "default")
    
    try:
        intent = state.get("intent", {})
        collected_info = state.get("collected_info", {})
        original_query = state.get("user_query", "")
        
        log_node_execution(thread_id, "Query Refinement", f"Refining: '{original_query}'")
        
        # Combine intent + collected answers into rich query
        product_type = intent.get("product_type", "product")
        structured_llm = llm.with_structured_output(QueryRefinementSchema, method='json_mode')
        result: QueryRefinementSchema = structured_llm.invoke(
            PROMPT.format(
                original_query=original_query,
                product_type=product_type,
                intent=intent,
                collected_info=collected_info
            )
        )
        
        refined = result.refined_query
        log_node_execution(thread_id, "Query Refinement", f"Result: '{refined}'")
        
        # Store as refined_query for use in data_retrieval
        state["refined_query"] = refined
        collected_info["refined_query"] = refined
        
        return state
        
    except Exception as e:
        log_error(thread_id, "Query Refinement Node", e)
        raise
