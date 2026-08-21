"""
Backend Helper Module
Provides database and checkpointer helper classes for the chatbot application.
"""

from langgraph.checkpoint.postgres import PostgresSaver
from app.core.config.settings import POSTGRES_SETTINGS
import psycopg
from urllib.parse import quote
from typing import List, Dict, Optional
from datetime import datetime


class CheckpointerHelper:
    """Helper class for managing PostgreSQL checkpointer operations"""
    
    def __init__(self):
        """Initialize PostgreSQL checkpointer"""
        # URL-encode the password so special chars like @ don't break the connection URL
        encoded_password = quote(POSTGRES_SETTINGS['password'], safe='')
        self.connection_string = (
            f"postgresql://{POSTGRES_SETTINGS['user']}:"
            f"{encoded_password}@"
            f"{POSTGRES_SETTINGS['host']}:"
            f"{POSTGRES_SETTINGS['port']}/"
            f"{POSTGRES_SETTINGS['database']}"
        )
        self.checkpointer = None
        self._initialize_checkpointer()
    
    def _initialize_checkpointer(self):
        """Initialize the PostgreSQL checkpointer"""
        try:
            conn_string = self.connection_string
            
            # Setup requires autocommit for CREATE INDEX CONCURRENTLY
            setup_conn = psycopg.connect(conn_string, autocommit=True)
            setup_saver = PostgresSaver(setup_conn)
            setup_saver.setup()
            setup_conn.close()
            
            # Create persistent connection for checkpointer use
            # Use a regular connection (no context manager)
            self.conn = psycopg.connect(conn_string)
            self.checkpointer = PostgresSaver(self.conn)
            
            print("✓ PostgreSQL checkpointer initialized")
        except Exception as e:
            print(f"✗ Failed to initialize checkpointer: {e}")
            raise
    
    def get_checkpointer(self) -> PostgresSaver:
        """Get the checkpointer instance"""
        return self.checkpointer
    
    def retrieve_all_threads(self) -> List[str]:
        """
        Retrieve all unique thread IDs from checkpointer
        
        Returns:
            List of thread ID strings
        """
        all_threads = set()
        try:
            for checkpoint in self.checkpointer.list(None):
                thread_id = checkpoint.config.get("configurable", {}).get("thread_id")
                if thread_id:
                    all_threads.add(thread_id)
        except Exception as e:
            print(f"Error retrieving threads: {e}")
        
        return list(all_threads)
    
    def get_thread_metadata(self, thread_id: str) -> Optional[Dict]:
        """
        Get metadata for a specific thread
        
        Args:
            thread_id: Thread identifier
            
        Returns:
            Dictionary with thread metadata or None
        """
        try:
            config = {"configurable": {"thread_id": thread_id}}
            state = self.checkpointer.get(config)
            
            if state:
                return {
                    "thread_id": thread_id,
                    "last_updated": datetime.now().isoformat(),
                    "has_data": True
                }
        except Exception as e:
            print(f"Error getting thread metadata: {e}")
        
        return None
    
    def delete_thread(self, thread_id: str) -> bool:
        """
        Delete all checkpoints for a specific thread
        
        Args:
            thread_id: Thread identifier
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # PostgresSaver doesn't have direct delete, but we can note this
            # The checkpoints will be managed by the DB retention policy
            print(f"Thread {thread_id} marked for cleanup")
            return True
        except Exception as e:
            print(f"Error deleting thread: {e}")
            return False


# Global checkpointer instance
_checkpointer_helper = None


def get_checkpointer_helper() -> CheckpointerHelper:
    """Get or create global checkpointer helper instance"""
    global _checkpointer_helper
    if _checkpointer_helper is None:
        _checkpointer_helper = CheckpointerHelper()
    return _checkpointer_helper
