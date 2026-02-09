from langchain_core.prompts import ChatPromptTemplate
from app.core.config.llm_provider import load_llm
from app.core.prompt.response_generator_prompt import response_generator_prompt
from app.core.prompt.web_extract_prompt import web_extract_prompt
from app.tools.system_tools import Tools
from app.schemas.pydantic_output_schemas.product_filter_schema import ProductMatchSchema
from app.schemas.pydantic_output_schemas.web_extraction_schema import WebExtractionSchema
from app.core.prompt.filter_prompt import filter_prompt
from app.core.logging.utils import log_node_execution, log_error
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv(), override=True)

llm = load_llm()
RESPONSE_PROMPT = response_generator_prompt()
WEB_EXTRACT_PROMPT = web_extract_prompt()
FILTER_PROMPT = filter_prompt()

tools = Tools()
web_search = tools.web_search


def response_generator_node(state, config):
    """Filter products and generate response, with web search fallback"""
    
    thread_id = config.get("configurable", {}).get("thread_id", "default")
    
    try:
        data = state.get("final_output", {})
        original_query = state.get("original_user_query", state["user_query"])
        collected_info = state.get("collected_info", {})
        
        log_node_execution(thread_id, "Response Generator", f"Processing query: '{original_query}'")
        
        # Step 1: Filter products to match user's specific request
        all_products = data.get("products", [])
        
        if all_products:
            log_node_execution(thread_id, "Response Generator", f"Filtering {len(all_products)} products")
            
            structured_llm = llm.with_structured_output(ProductMatchSchema, method='json_mode')
            filtered: ProductMatchSchema = structured_llm.invoke(
                FILTER_PROMPT.format(
                    original_query=original_query,
                    collected_info=collected_info,
                    products=all_products
                )
            )
                
            matching_products = filtered.matching_products
            has_matches = filtered.has_matches
            log_node_execution(thread_id, "Response Generator", f"Found {len(matching_products)} matches")
        else:
            matching_products = []
            has_matches = False
        
        # Step 2: Web search fallback if no matches
        if not has_matches or not matching_products:
            log_node_execution(thread_id, "Response Generator", "No matches, using web search")
            try:
                # Use refined query + shopping keywords for better results
                # Check state first, then collected_info (as backup)
                search_query = state.get("refined_query") or collected_info.get("refined_query") or original_query
                shopping_query = f"buy {search_query} price"
                
                log_node_execution(thread_id, "Response Generator", f"Searching web for: '{shopping_query}'")
                
                # Log which search tool is being used
                import os
                tool_name = "Google Search (Serper)" if os.environ.get("SERPER_API_KEY") else "DuckDuckGo"
                log_node_execution(thread_id, "Response Generator", f"Using Tool: {tool_name}")
                
                raw_results = web_search.invoke({"query": shopping_query})
                log_node_execution(thread_id, "Response Generator", f"Web search returned {len(raw_results) if raw_results else 0} chars")
                
                structured_llm = llm.with_structured_output(WebExtractionSchema, method='json_mode')
                extraction: WebExtractionSchema = structured_llm.invoke(
                    WEB_EXTRACT_PROMPT.format(search_results=raw_results)
                )
                web_products = [p.model_dump() for p in extraction.products]
                
                log_node_execution(thread_id, "Response Generator", f"Extracted {len(web_products)} products from web")
                matching_products = web_products
            except Exception as e:
                log_error(thread_id, "Web Search", e)
                matching_products = []
        
        # Step 3: Generate final response
        response = llm.invoke(
            RESPONSE_PROMPT.format(
                user_query=original_query,
                collected_info=collected_info,
                products=matching_products
            )
        )
        
        final_response = str(response.content) if hasattr(response, 'content') else str(response)
        log_node_execution(thread_id, "Response Generator", "Generated final response")
        
        state["final_output"] = {
            "response": final_response,
            "products": matching_products,
            "source": "web" if not all_products else "database"
        }
        
        # Store for memory
        state["collected_info"]["products"] = matching_products
        state["collected_info"]["source"] = "web" if not all_products else "database"
        
        return state
        
    except Exception as e:
        log_error(thread_id, "Response Generator Node", e)
        raise
