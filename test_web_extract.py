import sys
import json
sys.path.append("/home/vedant/Desktop/Personal-Projects/Trust_Cart_AI/AUTONOMOUS_PRODUCT_ASSISTANCE_AGENTIC_SYSTEM")

from app.core.config.llm_provider import load_llm
from app.tools.system_tools import Tools
from app.core.prompt.web_extract_prompt import web_extract_prompt
from app.schemas.pydantic_output_schemas.web_extraction_schema import WebExtractionSchema

llm = load_llm()
WEB_EXTRACT_PROMPT = web_extract_prompt()
tools = Tools()

print("Searching web...")
raw_results = tools.web_search.invoke({"query": "best nike running shoes"})
print(f"Raw results length: {len(raw_results)}")
print(f"Raw results snippet: {raw_results[:500]}...")

print("Extracting products...")
structured_llm = llm.with_structured_output(WebExtractionSchema, method='json_mode')
extraction = structured_llm.invoke(WEB_EXTRACT_PROMPT.format(search_results=raw_results))

print("\n--- Extracted Products ---")
for i, p in enumerate(extraction.products):
    print(f"Product {i+1}:")
    print(f"  Title: {p.title}")
    print(f"  URL: {p.url}")
    print(f"  Thumbnail: {p.thumbnail}")
    print(f"  Price: {p.price}")
