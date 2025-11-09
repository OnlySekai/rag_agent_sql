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
    can_collect_more: bool = Field(
        description="Whether it's possible to collect additional helpful information from available tables"
    )
    suggested_next_query: Optional[str] = Field(
        default=None,
        description="Brief description of what the next query should retrieve, if more data can be collected"
    )
