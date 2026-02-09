from pydantic import BaseModel, Field


class DeciderSchema(BaseModel):
    """Schema for decider node output"""
    mode: str = Field(..., description="Either 'conversation' or 'agentic'")
    reasoning: str = Field(..., description="Brief explanation of the routing decision")
    refined_query: str = Field(..., description="Context-aware refined query that clearly states what the user wants (e.g., 'User wants to find running shoes for athletic use')")
