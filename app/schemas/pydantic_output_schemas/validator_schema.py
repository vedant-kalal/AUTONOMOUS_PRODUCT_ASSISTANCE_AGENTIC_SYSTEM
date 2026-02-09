from pydantic import BaseModel, Field
from typing import Optional, List


class ValidatorSchema(BaseModel):
    """Schema for validator output"""
    validated: bool = Field(..., description="Whether the intent is valid")
    missing_info: List[str] = Field(default_factory=list, description="List of missing fields")
    reason: Optional[str] = Field(None, description="Explanation of validation result")
