ALLOWED_CATEGORIES = {
    "beauty",
    "groceries",
    "fragrances",
    "furniture"
}

MEMORY_FILE = "memory/long_term_memory.json"
MAX_RECENT_MESSAGES = 6  

DB_URI = "postgresql://postgres:Vedank10%40@localhost:5432/chatbot_memory?sslmode=disable"


# PostgreSQL settings for checkpointer
POSTGRES_SETTINGS = {
    "host": "localhost",
    "port": "5432",
    "database": "chatbot_memory",
    "user": "postgres",
    "password": "Vedank10@"
}

# Namespaces
STM_NAMESPACE = ("conversation",)
LTM_NAMESPACE = ("user", "u1", "details")  # user-scoped
SUMMARY_NAMESPACE = ("conversation", "summary")  # Conversation summary

# Cross-thread, single-user namespaces (this app has no auth, so "u1" is the only user)
USER_PROFILE_NAMESPACE = ("user", "u1", "profile")  # Durable preferences (size, skin type, favorite brands)
FEEDBACK_NAMESPACE = ("user", "u1", "feedback")  # Thumbs up/down on past recommendations
WISHLIST_NAMESPACE = ("user", "u1", "wishlist")  # Saved-for-later products
SHARE_NAMESPACE = ("shared_results",)  # Public read-only shareable snapshots, keyed by share token

MAX_STM_MESSAGES = 6
RECENT_WINDOW_SIZE = 100  # Keep last 100 messages to prevent UI history loss

# ----------------------------
# LLM Model Selection (OpenRouter)
# ----------------------------
# "Main" model: used for generation-heavy steps (question crafting, response writing)
DEFAULT_MAIN_MODEL = "openai/gpt-4o"
# "Fast" model: used for cheap/quick classification steps (routing, intent extraction, validation)
DEFAULT_FAST_MODEL = "openai/gpt-4o-mini"
