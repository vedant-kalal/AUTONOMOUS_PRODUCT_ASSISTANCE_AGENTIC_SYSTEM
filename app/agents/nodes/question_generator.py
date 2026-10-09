import json

from app.core.config.llm_provider import load_llm
from app.core.prompt.info_collector_prompt import info_collector_prompt, gift_info_collector_prompt
from app.schemas.pydantic_output_schemas.question_schema import QuestionList
from app.memory.memory_store import Memory_Functions
from app.core.logging.utils import log_node_execution

llm = load_llm()
PROMPT = info_collector_prompt()
GIFT_PROMPT = gift_info_collector_prompt()


def question_generator_node(state, config):
    """Generate clarifying questions and return normally (no interrupt here).

    This MUST be a separate node from the one that calls interrupt(): LangGraph replays a
    node's code from the top every time it resumes from an interrupt inside it, which would
    silently regenerate a fresh (differently-worded) question list on every resume and break
    any downstream matching against the original questions. Splitting generation (which
    completes and checkpoints normally) from the interrupt call (which is safe to replay,
    since it does no LLM calls) avoids that.
    """
    thread_id = config.get("configurable", {}).get("thread_id", "default")
    is_gift = bool(state.get("is_gift"))

    intent = state.get("intent", {})
    product_type = intent.get("product_type", "product")

    known_preferences = {} if is_gift else Memory_Functions.get_user_profile()

    log_node_execution(thread_id, "Question Generator", f"Generating questions for '{product_type}' (gift={is_gift})")

    user_query = state.get("original_user_query", state.get("user_query", ""))
    prompt = GIFT_PROMPT if is_gift else PROMPT

    structured_llm = llm.with_structured_output(QuestionList, method='json_mode')
    format_kwargs = dict(
        user_query=user_query,
        product_type=product_type,
        intent=intent,
        optimization_goal=state.get("optimization_goal", "Balanced")
    )
    if not is_gift:
        format_kwargs["known_preferences"] = json.dumps(known_preferences, default=str) if known_preferences else "(none yet)"

    result: QuestionList = structured_llm.invoke(prompt.format(**format_kwargs))

    questions_data = [q.model_dump() for q in result.list_of_questions]
    log_node_execution(thread_id, "Question Generator", f"Generated {len(questions_data)} questions")

    state["generated_questions"] = questions_data
    state["question_durability"] = {q["question"]: q["durable"] for q in questions_data}
    state["known_preferences"] = known_preferences

    return state
