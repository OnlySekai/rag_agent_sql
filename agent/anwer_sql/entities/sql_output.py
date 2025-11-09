from agent.create_db.entities.table_info import TableOutput
from typing import Dict
from pydantic import BaseModel, Field

class SQLQueryOutput(BaseModel):
    """Output structure for SQL query generation"""
    sql: str = Field(description="The SQL query to execute")
    tables: Dict[str, str] = Field(
        description="Dictionary mapping table names to their file paths"
    )
    knowledge_summary: str = Field(
        description="Brief summary of what information/knowledge this query will retrieve to answer the question"
    )
