from langgraph.types import interrupt
from app.core.config.llm_provider import load_llm
from app.core.prompt.info_collector_prompt import info_collector_prompt
from app.schemas.pydantic_output_schemas.question_schema import QuestionList
from app.core.logging.utils import log_node_execution, log_error, log_qa_session

llm = load_llm()
PROMPT = info_collector_prompt()


def info_collector_node(state, config):
    """Generate domain-specific questions based on product type and pause for user input"""
    
    thread_id = config.get("configurable", {}).get("thread_id", "default")
    
    try:
        intent = state.get("intent", {})
        product_type = intent.get("product_type", "product")
        
        # Check if questions were already generated (to avoid re-generation on resume)
        questions = state.get("generated_questions", [])
        
        if not questions:
            log_node_execution(thread_id, "Info Collector", f"Generating questions for '{product_type}'")
            
            user_query = state.get("original_user_query", state.get("user_query", ""))
            
            # Use LangChain's native structured output with JSON mode
            structured_llm = llm.with_structured_output(QuestionList, method='json_mode')
            result: QuestionList = structured_llm.invoke(
                PROMPT.format(
                    user_query=user_query,
                    product_type=product_type,
                    intent=intent
                )
            )
            questions = result.list_of_questions
            log_node_execution(thread_id, "Info Collector", f"Generated {len(questions)} questions")
            # Persist generated questions in state
            state["generated_questions"] = questions
        else:
            log_node_execution(thread_id, "Info Collector", f"Using existing questions ({len(questions)})")
            

        
        # Use LangGraph interrupt to pause workflow and collect answers
        collected_answers = interrupt(questions)
        
        # Log Q&A session
        qa_pairs = [{"question": q, "answer": collected_answers.get(q, "")} for q in questions]
        log_qa_session(thread_id, qa_pairs)
        
        # Store the collected information
        state["collected_info"] = collected_answers
        log_node_execution(thread_id, "Info Collector", f"Collected {len(collected_answers)} answers")
        
        return state
        
    except Exception as e:
        # Ignore LangGraph interrupts, they are control flow signals
        if "GraphInterrupt" in str(type(e)):
            raise e
            
        log_error(thread_id, "Info Collector Node", e)
        raise
