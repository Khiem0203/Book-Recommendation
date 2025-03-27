from pydantic import BaseModel
from typing import List, Optional

class Book(BaseModel):
    title: str
    authors: str
    published_year: Optional[int]
    average_rating: Optional[float]
    thumbnail: Optional[str]
    description: Optional[str]

class RecommendationResponse(BaseModel):
    results: List[Book]
