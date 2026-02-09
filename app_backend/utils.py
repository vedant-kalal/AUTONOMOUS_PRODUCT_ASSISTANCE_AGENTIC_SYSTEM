"""
Utility Module
Provides thread and session management utilities for the chatbot application.
"""

import uuid
from typing import List, Dict, Optional
from langchain_core.messages import HumanMessage, AIMessage
from app_backend.helper import get_checkpointer_helper


class ThreadManager:
    """Manager class for chat thread operations"""
    
    @staticmethod
    def generate_thread_id() -> str:
        """
        Generate a new unique thread ID
        
        Returns:
            UUID string as thread identifier
        """
        return str(uuid.uuid4())
    
    @staticmethod
    def get_all_threads() -> List[str]:
        """
        Retrieve all available thread IDs
        
        Returns:
            List of thread ID strings
        """
        helper = get_checkpointer_helper()
        return helper.retrieve_all_threads()
    
    @staticmethod
    def load_conversation(thread_id: str, workflow_app) -> List[Dict]:
        """
        Load conversation history for a specific thread
        
        Args:
            thread_id: Thread identifier
            workflow_app: The compiled workflow application
            
        Returns:
            List of message dictionaries with 'role' and 'content'
        """
        try:
            config = {"configurable": {"thread_id": thread_id}}
            state = workflow_app.get_state(config)
            
            # Extract messages from state if they exist
            messages = []
            if state and state.values:
                # Check different possible message storage locations
                if "messages" in state.values:
                    raw_messages = state.values["messages"]
                elif "conversation_history" in state.values:
                    raw_messages = state.values["conversation_history"]
                else:
                    return []
                
                # Convert to dict format
                for msg in raw_messages:
                    if isinstance(msg, HumanMessage):
                        messages.append({"role": "user", "content": msg.content})
                    elif isinstance(msg, AIMessage):
                        messages.append({"role": "assistant", "content": msg.content})
            
            return messages
        except Exception as e:
            print(f"Error loading conversation: {e}")
            return []
    
    @staticmethod
    def delete_thread(thread_id: str) -> bool:
        """
        Delete a thread and its associated data
        
        Args:
            thread_id: Thread identifier
            
        Returns:
            True if successful, False otherwise
        """
        helper = get_checkpointer_helper()
        return helper.delete_thread(thread_id)
    
    @staticmethod
    def get_thread_preview(thread_id: str, workflow_app) -> Optional[str]:
        """
        Get a preview/title for a thread based on first message
        
        Args:
            thread_id: Thread identifier
            workflow_app: The compiled workflow application
            
        Returns:
            Preview string or thread_id if no messages
        """
        messages = ThreadManager.load_conversation(thread_id, workflow_app)
        
        if messages and len(messages) > 0:
            # Use first user message as preview
            first_msg = messages[0]["content"]
            # Truncate to 50 chars
            preview = first_msg[:50] + "..." if len(first_msg) > 50 else first_msg
            return preview
        
        return thread_id[:8]  # Return first 8 chars of UUID


class SessionManager:
    """Manager class for session state operations (for Streamlit)"""
    
    @staticmethod
    def reset_chat(session_state: Dict, workflow_app) -> str:
        """
        Reset chat to a new thread
        
        Args:
            session_state: Streamlit session state dictionary
            workflow_app: The compiled workflow application
            
        Returns:
            New thread ID
        """
        thread_id = ThreadManager.generate_thread_id()
        session_state["thread_id"] = thread_id
        session_state["message_history"] = []
        
        # Add to thread list if not already there
        if "chat_threads" not in session_state:
            session_state["chat_threads"] = []
        
        if thread_id not in session_state["chat_threads"]:
            session_state["chat_threads"].insert(0, thread_id)
        
        return thread_id
    
    @staticmethod
    def switch_thread(session_state: Dict, thread_id: str, workflow_app):
        """
        Switch to a different thread
        
        Args:
            session_state: Streamlit session state dictionary
            thread_id: Thread to switch to
            workflow_app: The compiled workflow application
        """
        session_state["thread_id"] = thread_id
        
        # Load conversation history
        messages = ThreadManager.load_conversation(thread_id, workflow_app)
        session_state["message_history"] = messages
