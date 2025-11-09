from pydantic import BaseModel, Field
from typing import Optional

class SufficiencyCheck(BaseModel):
    """Structured output for data sufficiency check"""
    has_enough_data: bool = Field(
        description="Whether the collected data is sufficient to answer the question completely"
    )
    reasoning: str = Field(
        description="Explanation of why the data is sufficient or what is missing"
    )
    missing_info: Optional[str] = Field(
        default=None,
        description="Specific description of what data is missing, if any"
    )
    final_answer: Optional[str] = Field(
        description="Complete, concise answer to the original user question"
    )
