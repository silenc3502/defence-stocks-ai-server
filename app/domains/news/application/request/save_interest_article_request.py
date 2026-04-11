from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class SaveInterestArticleRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    source: Optional[str] = Field(None, max_length=255)
    link: str = Field(..., min_length=1, max_length=512)
    published_at: Optional[datetime] = None
