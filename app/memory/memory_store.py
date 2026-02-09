
from typing import List, Dict, Any, Optional
from datetime import datetime

from langchain_core.messages import HumanMessage, AIMessage, RemoveMessage, BaseMessage
from langgraph.store.postgres import PostgresStore

from app.core.config.settings import STM_NAMESPACE, LTM_NAMESPACE, SUMMARY_NAMESPACE, MAX_STM_MESSAGES, RECENT_WINDOW_SIZE, DB_URI
from app.core.logging.base import get_logger


# ======================================================
# SHORT TERM MEMORY (STM) + ROLLING SUMMARY
# ======================================================




class Memory_Functions:
    """
    Handles Short-Term Memory (STM), Long-Term Memory (LTM), and Rolling Summary
    Thread-safe implementation using fresh context per operation.
    """

    _llm: Any = None  # For summarization - safe to cache LLM client usually

    @classmethod
    def _get_llm(cls) -> Any:
        """Lazy load LLM for summarization"""
        if cls._llm is None:
            from app.core.config.llm_provider import load_llm
            cls._llm = load_llm()
        return cls._llm

    # ----------------------------
    # SUMMARY MANAGEMENT
    # ----------------------------
    @classmethod
    def get_summary(cls, thread_id: str = "default") -> Optional[str]:
        """Get the current conversation summary for a specific thread"""
        with PostgresStore.from_conn_string(DB_URI) as store:
            store.setup()
            namespace = SUMMARY_NAMESPACE + (thread_id,)
            items = list(store.search(namespace))
            
            if not items:
                return None
            
            latest = items[-1]
            return latest.value.get("summary", "")

    @classmethod
    def update_summary(cls, new_messages: List[BaseMessage], thread_id: str = "default") -> None:
        """Update summary by appending new messages to existing summary"""
        with PostgresStore.from_conn_string(DB_URI) as store:
            store.setup()
            llm = cls._get_llm()
            namespace = SUMMARY_NAMESPACE + (thread_id,)
            
            # Get current summary
            items = list(store.search(namespace))
            current_summary = items[-1].value.get("summary", "") if items else ""
            
            # Format new messages
            new_content = "\n".join([
                f"{msg.type}: {msg.content}" for msg in new_messages
            ])
            
            # Generate updated summary
            summary_prompt = f"""You are summarizing a conversation between a user and a product assistant.

**Current Summary:**
{current_summary if current_summary else "(No previous summary)"}

**New Messages to Add:**
{new_content}

**Task:** Create a concise, cumulative summary that:
1. Preserves key information from the current summary
2. Adds important details from the new messages
3. Focuses on: products discussed, user preferences, questions asked, recommendations made
4. Keeps it under 200 words

**Updated Summary:**"""
            
            updated_summary = llm.invoke(summary_prompt).content.strip()
            
            # Store updated summary
            store.put(
                namespace,
                key=str(datetime.utcnow().timestamp()),
                value={
                    "summary": updated_summary,
                    "updated_at": datetime.utcnow().isoformat()
                }
            )
            
            logger = get_logger('memory', thread_id)
            logger.info(f"Summary updated ({len(updated_summary)} chars)")

    # ----------------------------
    # STM with Rolling Window
    # ----------------------------
    @classmethod
    def add_recent_message(cls, message: BaseMessage, thread_id: str = "default") -> None:
        """Add message and maintain rolling window with auto-summarization"""
        with PostgresStore.from_conn_string(DB_URI) as store:
            store.setup()
            namespace = STM_NAMESPACE + (thread_id,)

            # Add new message
            store.put(
                namespace,
                key=str(datetime.utcnow().timestamp()),
                value={
                    "type": message.__class__.__name__,
                    "content": message.content,
                },
            )

            # Get all messages
            items = list(store.search(namespace))
            total_count = len(items)
            
            # If we exceed the window, summarize old messages and remove them
            if total_count > RECENT_WINDOW_SIZE:
                messages_to_summarize = total_count - RECENT_WINDOW_SIZE
                
                # Get oldest messages
                # Sort first to be safe
                items.sort(key=lambda x: x.key)
                old_items = items[:messages_to_summarize]
                old_messages = []
                
                for it in old_items:
                    data = it.value
                    if data["type"] == "HumanMessage":
                        old_messages.append(HumanMessage(content=data["content"]))
                    else:
                        old_messages.append(AIMessage(content=data["content"]))
                
                # Update summary with these messages (Using separate context logic inside calls is safe but nested? 
                # Better to call update logic directly or allow update_summary to handle context? 
                # calling cls.update_summary creates NEW context. Safest is sequential.)
                
                if old_messages:
                    # We accept the overhead of reopening connection for summary update to ensure safety
                    cls.update_summary(old_messages, thread_id)
                    logger = get_logger('memory', thread_id)
                    logger.info(f"Moved {len(old_messages)} messages to summary")
                
                # Delete old messages
                for it in old_items:
                    store.delete(namespace, key=it.key)

    @classmethod
    def get_recent_messages(cls, thread_id: str = "default") -> List[BaseMessage]:
        with PostgresStore.from_conn_string(DB_URI) as store:
            store.setup()
            messages: List[BaseMessage] = []
            namespace = STM_NAMESPACE + (thread_id,)

            items = list(store.search(namespace))
            items.sort(key=lambda x: x.key)
            
            for it in items:
                data = it.value
                if not data:
                    continue

                if data["type"] == "HumanMessage":
                    messages.append(HumanMessage(content=data["content"]))
                else:
                    messages.append(AIMessage(content=data["content"]))

            return messages

    @classmethod
    def clear_recent_messages(cls, thread_id: str = "default") -> None:
        with PostgresStore.from_conn_string(DB_URI) as store:
            store.setup()
            namespace = STM_NAMESPACE + (thread_id,)
            for it in store.search(namespace):
                store.delete(namespace, key=it.key)

    @classmethod
    def clear_summary(cls, thread_id: str = "default") -> None:
        with PostgresStore.from_conn_string(DB_URI) as store:
            store.setup()
            namespace = SUMMARY_NAMESPACE + (thread_id,)
            for it in store.search(namespace):
                store.delete(namespace, key=it.key)

    # ----------------------------
    # LTM
    # ----------------------------
    @classmethod
    def store_long_term_memory(cls, data: Dict[str, Any], thread_id: str = "default") -> None:
        with PostgresStore.from_conn_string(DB_URI) as store:
            store.setup()
            namespace = LTM_NAMESPACE + (thread_id,)

            store.put(
                namespace,
                key=str(datetime.utcnow().timestamp()),
                value={
                    "data": data,
                    "stored_at": datetime.utcnow().isoformat(),
                },
            )

    @classmethod
    def get_long_term_memory(cls, limit: int = 1, thread_id: str = "default") -> List[Dict[str, Any]]:
        with PostgresStore.from_conn_string(DB_URI) as store:
            store.setup()
            namespace = LTM_NAMESPACE + (thread_id,)
            items = list(store.search(namespace))

            return [it.value["data"] for it in items[-limit:]]

    @classmethod
    def clear_long_term_memory(cls, thread_id: str = "default") -> None:
        with PostgresStore.from_conn_string(DB_URI) as store:
            store.setup()
            namespace = LTM_NAMESPACE + (thread_id,)
            for it in store.search(namespace):
                store.delete(namespace, key=it.key)
