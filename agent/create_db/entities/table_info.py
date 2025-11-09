from pydantic import BaseModel, Field
from agent.create_db.entities.table_schema import SchemaInfo
from typing import List
# Define the Pydantic model for the structured output
class TableOutput(BaseModel):
    """Structured output for table processing."""
    table_name: str = Field(description="The name of the table.")
    csv_content: str = Field(description="The flattened CSV content of the table.")
    schema_info: List[SchemaInfo] = Field(description="Inferred schema with column details. Provide a list of dictionaries, where each dictionary represents a column and has keys 'column_name', 'data_type', 'nullable', 'is_primary', and 'is_foreign_key'.")
    summary: str = Field(description="A summary of the table content for retrieval tasks.")
    path: str