from pydantic import BaseModel, Field


class QueryRefinementSchema(BaseModel):
    """Schema for refined query output"""
    refined_query: str = Field(..., description="Refined, search-optimized query with product type and specifications")
