from pydantic import BaseModel, Field
from typing import List


class QuestionItem(BaseModel):
    """A single clarifying question"""
    question: str = Field(description="The question text to ask the user")
    durable: bool = Field(
        description="True if this asks about a lasting personal trait (size, skin type, favorite brand) "
                     "worth remembering for future purchases. False if it's specific to this one purchase "
                     "(budget, color for this item, occasion)."
    )


class QuestionList(BaseModel):
    """Schema for batch question generation by info_collector"""
    list_of_questions: List[QuestionItem] = Field(
        description="List of questions to ask the user to collect missing information"
    )
