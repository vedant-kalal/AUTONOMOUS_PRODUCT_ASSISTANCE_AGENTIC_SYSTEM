from pydantic import BaseModel, Field
from typing import Optional


class IntentSchema(BaseModel):
    """Schema for intent analyzer output"""
    product_type: Optional[str] = Field(None, description="The specific product user wants (e.g., 'laptop', 'tv', 'shoes')")
    product_category: Optional[str] = Field(None, description="One of: beauty, groceries, fragrances, furniture, or null")
    max_price: Optional[float] = Field(None, description="Maximum price/budget mentioned by user")
