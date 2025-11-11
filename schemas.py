"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field
from typing import Optional, List

# Example schemas (kept for reference)
class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product" (lowercase of class name)
    """
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")

# Anime app schemas
class Anime(BaseModel):
    """
    Anime collection schema
    Collection name: "anime"
    """
    title: str = Field(..., description="Anime title")
    description: Optional[str] = Field(None, description="Short description")
    cover_url: Optional[str] = Field(None, description="Cover image URL")
    tags: Optional[List[str]] = Field(default_factory=list, description="List of tags/genres")
    year: Optional[int] = Field(None, description="Release year")
    external_url: Optional[str] = Field(None, description="External link to watch on another site (e.g., HiAnime)")

class Episode(BaseModel):
    """
    Episode collection schema
    Collection name: "episode"
    """
    anime_id: str = Field(..., description="Related anime ObjectId as string")
    number: int = Field(..., ge=1, description="Episode number")
    title: str = Field(..., description="Episode title")
    stream_url: str = Field(..., description="Video stream URL")
    thumbnail_url: Optional[str] = Field(None, description="Episode thumbnail URL")
    duration: Optional[int] = Field(None, description="Duration in minutes")
    external_url: Optional[str] = Field(None, description="External link to this episode on another site (e.g., HiAnime)")

# The Flames database viewer will automatically read these schemas from GET /schema
