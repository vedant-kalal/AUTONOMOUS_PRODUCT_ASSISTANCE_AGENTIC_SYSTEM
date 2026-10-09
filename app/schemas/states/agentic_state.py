from typing import TypedDict, Optional, Dict, Any, List

class AgentState(TypedDict):
    user_query: str
    original_user_query: Optional[str]  # Store original query before refinement
    mode: Optional[str]
    supervisor_decision: Optional[str]
    intent: Optional[dict]
    missing_info: Optional[list]
    validated: Optional[bool]
    final_output: Optional[dict]
    pending_questions: Optional[list]  # List of questions to ask
    collected_info: Optional[dict]  # Dict of answers {question: answer}
    raw_data: Optional[List[Dict[str, Any]]]
    final_output: Optional[Dict[str, Any]]
    refined_query: Optional[str]  # Persist refined query explicitly
    generated_questions: Optional[List[str]]  # Persist generated questions to avoid regeneration on resume
    optimization_goal: Optional[str]  # Personality slider preference
    is_gift: Optional[bool]  # True when shopping for someone else ("gift-finder mode")
    known_preferences: Optional[Dict[str, Any]]  # Durable profile facts (size, skin type, brand) pre-filled from memory
    question_durability: Optional[Dict[str, bool]]  # question text -> is this a durable/profile-worthy preference
    feedback_context: Optional[str]  # Summary of past thumbs up/down, injected into recommendation prompts
    product_reasons: Optional[Dict[str, str]]  # product title -> short "why this" explanation
