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

MAX_STM_MESSAGES = 6
RECENT_WINDOW_SIZE = 100  # Keep last 100 messages to prevent UI history loss