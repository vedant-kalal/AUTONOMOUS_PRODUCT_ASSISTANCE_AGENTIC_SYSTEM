from pydantic import BaseModel, Field
from typing import List, Any


class ProductMatchSchema(BaseModel):
    """Schema for product matching output"""
    matching_products: List[Any] = Field(
        default_factory=list,
        description="List of product objects that match the user's request"
    )
    has_matches: bool = Field(..., description="Whether any products matched the criteria")
