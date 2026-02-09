from pydantic import BaseModel, Field
from typing import List

class QuestionList(BaseModel):
    """Schema for batch question generation by info_collector"""
    list_of_questions: List[str] = Field(
        description="List of questions to ask the user to collect missing information"
    )
