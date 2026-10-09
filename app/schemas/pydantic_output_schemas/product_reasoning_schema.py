from pydantic import BaseModel, Field
from typing import List


class ProductReason(BaseModel):
    """Why a single product was recommended, keyed by its exact title"""
    title: str = Field(description="Exact product title, matching one of the recommended products")
    why: str = Field(description="One or two crisp sentences on why this product fits the user's request")


class ProductReasoningSchema(BaseModel):
    """Schema for the 'Why this?' structured explanation pass"""
    reasons: List[ProductReason] = Field(default_factory=list)
