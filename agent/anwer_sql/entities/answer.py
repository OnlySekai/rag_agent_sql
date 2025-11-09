from pydantic import BaseModel, Field
from typing import List
class KnowledgeAnswer(BaseModel):
    """Answer for each knowledge question"""
    knowledge_question: str = Field(description="The knowledge summary/question from the query")
    answer: str = Field(description="Direct answer based on the query results and data")
    supporting_data: str = Field(description="Key data points that support this answer")


class FinalAnswerOutput(BaseModel):
    """Structured output for final answer generation"""
    knowledge_answers: List[KnowledgeAnswer] = Field(
        description="Answers to each knowledge question from the queries, based on actual data"
    )
    final_answer: str = Field(
        description="Complete, concise answer to the original user question"
    )