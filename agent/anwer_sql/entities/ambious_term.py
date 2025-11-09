from pydantic import BaseModel, Field
from typing import List

class AmbiousTerm(BaseModel):
    """Detect the ambious term"""
    term: List[str] = Field(description="The ambious term")
    definition_questions: List[str] = Field(description="Question to definition terms")
