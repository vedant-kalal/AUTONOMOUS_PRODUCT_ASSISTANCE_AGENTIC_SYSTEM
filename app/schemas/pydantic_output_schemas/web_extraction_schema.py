from pydantic import BaseModel, Field
from typing import Optional, List


class Product(BaseModel):
    """Individual product schema"""
    title: str = Field(..., description="Product name")
    price: Optional[float] = Field(None, description="Product price")
    description: Optional[str] = Field(None, description="Product description")
    category: Optional[str] = Field(None, description="Product category")
    brand: Optional[str] = Field(None, description="Product brand")
    url: Optional[str] = Field(None, description="Product URL")


class WebExtractionSchema(BaseModel):
    """Schema for web extraction output"""
    products: List[Product] = Field(default_factory=list, description="List of extracted products")
