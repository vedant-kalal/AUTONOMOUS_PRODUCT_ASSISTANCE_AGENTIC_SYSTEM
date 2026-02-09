"""
Logging Utilities
Helper functions for common logging patterns
"""

from app.core.logging.base import get_logger



def log_chat_start(thread_id: str, user_input: str):
    """Log start of chat session"""
    logger = get_logger('app', thread_id)
    logger.info("=" * 80)
    logger.info(f"🟢 NEW CHAT | User: {user_input}")
    logger.info("=" * 80)


def log_chat_response(thread_id: str, response: str):
    """Log AI response"""
    logger = get_logger('app', thread_id)
    logger.info("-" * 80)
    logger.info(f"🤖 AI Response:\n{response}")
    logger.info("-" * 80)


def log_node_execution(thread_id: str, node_name: str, details: str = ""):
    """Log node execution"""
    logger = get_logger('workflow', thread_id)
    logger.info(f"⚙️  {node_name}: {details}")


def log_decision(thread_id: str, query: str, mode: str, reasoning: str):
    """Log decider decision"""
    logger = get_logger('workflow', thread_id)
    logger.info(f"🎯 Decision: Query='{query}' → Mode={mode}")
    logger.info(f"   Reasoning: {reasoning}")


def log_qa_session(thread_id: str, qa_pairs: list):
    """Log Q&A session"""
    logger = get_logger('app', thread_id)
    logger.info("┌─ Q&A SESSION ────────────────────────────────────────┐")
    for i, pair in enumerate(qa_pairs, 1):
        q = pair.get("question", "")
        a = pair.get("answer", "")
        logger.info(f"│ Q{i}: {q}")
        logger.info(f"│ A{i}: {a}")
        if i < len(qa_pairs):
            logger.info("│ " + "─" * 54)
    logger.info("└──────────────────────────────────────────────────────┘")


def log_memory_operation(thread_id: str, operation: str, details: str = ""):
    """Log memory operation"""
    logger = get_logger('memory', thread_id)
    logger.info(f"💾 {operation}: {details}")


def log_error(thread_id: str, context: str, error: Exception):
    """Log error with traceback"""
    logger = get_logger('app', thread_id)
    import traceback
    logger.error(f"❌ ERROR in {context}: {str(error)}")
    logger.error(f"Traceback:\n{traceback.format_exc()}")
