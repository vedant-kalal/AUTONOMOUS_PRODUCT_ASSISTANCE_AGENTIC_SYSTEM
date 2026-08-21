from app.core.config.llm_provider import load_llm
from app.core.config.settings import ALLOWED_CATEGORIES
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from app.tools.system_tools import Tools
from app.core.prompt.web_extract_prompt import web_extract_prompt
from app.core.prompt.parse_prompt import parse_prompt
from app.core.logging.base import get_logger

from app.tools.system_tools import Tools
from app.core.prompt.web_extract_prompt import web_extract_prompt
from app.core.prompt.parse_prompt import parse_prompt


tools = Tools()
web_search = tools.web_search
fetch_products = tools.fetch_products
filter_by_price = tools.filter_by_price

llm = load_llm()
parser = JsonOutputParser()
PARSE_PROMPT = parse_prompt()
WEB_EXTRACT_PROMPT = web_extract_prompt()


# -------- HELPER FUNCTION -------- #

def filter_by_brand(products, collected_info):
    """Filter products to match user's brand preference"""
    if not collected_info:
        return products
    
    # Extract brand from collected_info
    brand_preference = None
    for key, value in collected_info.items():
        if value and isinstance(value, str):
            key_lower = key.lower()
            if 'brand' in key_lower or 'manufacturer' in key_lower or 'preference' in key_lower:
                brand_preference = value.lower().strip()
                break
    
    if not brand_preference:
        return products
    
    # Filter products by brand
    filtered = []
    for product in products:
        product_title = (product.get('title') or '').lower()
        product_brand = (product.get('brand') or '').lower()
        
        # Check if brand is in title or brand field
        if brand_preference in product_title or brand_preference in product_brand:
            filtered.append(product)
    
    # Note: logging removed from helper function since it doesn't have thread_id
    if filtered:
        return filtered
    else:
        return products


# -------- NODE -------- #

def data_retrieval_node(state, config):
    thread_id = config.get("configurable", {}).get("thread_id", "default")
    
    try:
        from app.core.logging.utils import log_node_execution, log_error
        
        user_query = state.get("refined_query") or state["user_query"]
        intent = state.get("intent", {})
        collected_info = state.get("collected_info", {})
        
        log_node_execution(thread_id, "Data Retrieval", f"Processing query: '{user_query}'")

        
        # Extract from intent
        category = intent.get("product_category")
        max_price = intent.get("max_price")
        # Construct a highly targeted search query using the original query + user's answers
        search_terms = [user_query]
        for key, val in collected_info.items():
            if val and isinstance(val, str) and val.lower() not in ["no", "none", "n/a"]:
                search_terms.append(val)
        
        search_query = " ".join(search_terms)
        log_node_execution(thread_id, "Data Retrieval", f"Constructed search query: '{search_query}'")
        
        # 2️⃣ Decide flow
        if not category or category not in ALLOWED_CATEGORIES:
            log_node_execution(thread_id, "Data Retrieval", "Category not in allowed list → Web Search")
            # ---- WEB FALLBACK ----
            raw_results = web_search.invoke({"query": search_query})

            # Use LangChain's native structured output for web extraction
            from app.schemas.pydantic_output_schemas.web_extraction_schema import WebExtractionSchema
            
            try:
                structured_llm = llm.with_structured_output(WebExtractionSchema, method='json_mode')
                extraction: WebExtractionSchema = structured_llm.invoke(
                    WEB_EXTRACT_PROMPT.format(search_results=raw_results)
                )
                products = [p.model_dump() for p in extraction.products]
            except Exception as e:
                log_error(thread_id, "Web Extraction (Direct)", e)
                # Fallback: create a generic product from query
                products = [{
                    "title": f"Product matching '{user_query}'",
                    "price": None,
                    "description": "No detailed information available from web search"
                }]
            
            # Filter by brand if user specified one
            products = filter_by_brand(products, collected_info)

            state["final_output"] = {
                "source": "web",
                "products": products
            }
            state["raw_data"] = products  # Store for LTM
            log_node_execution(thread_id, "Data Retrieval", f"Retrieved {len(products)} products from web")
            return state

        # ---- API FLOW ----
        log_node_execution(thread_id, "Data Retrieval", f"Category '{category}' allowed → API Search")
        products = fetch_products.invoke({"category": category})
        products = filter_by_price.invoke({"products": products, "max_price": max_price})

        # ---- FALLBACK CHECK ----
        if not products:
            log_node_execution(thread_id, "Data Retrieval", "API returned 0 products → Fallback to Web")
            raw_results = web_search.invoke({"query": search_query})
            try:
                products = (WEB_EXTRACT_PROMPT | llm | parser).invoke({
                    "search_results": raw_results
                })["products"]
            except Exception as e:
                log_error(thread_id, "Web Extraction (Fallback)", e)
                # Fallback: create a generic product from query
                products = [{
                    "title": f"Product matching '{user_query}'",
                    "price": None,
                    "description": "No detailed information available from web search"
                }]
            
            # Filter by brand if user specified one
            products = filter_by_brand(products, collected_info)
            
            state["final_output"] = {
                "source": "web_fallback",
                "products": products
            }
            state["raw_data"] = products  # Store for LTM
            log_node_execution(thread_id, "Data Retrieval", f"Retrieved {len(products)} products from web fallback")
            return state

        state["final_output"] = {
            "source": "api",
            "category": category,
            "max_price": max_price,
            "products": products
        }
        state["raw_data"] = products  # Store for LTM
        log_node_execution(thread_id, "Data Retrieval", f"Retrieved {len(products)} products from API")

        return state
        
    except Exception as e:
        # Need to import log_error locally if not top-level, or assume imported
        from app.core.logging.utils import log_error
        log_error(thread_id, "Data Retrieval Node", e)
        raise
