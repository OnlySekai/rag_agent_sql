from pydantic import BaseModel, Field
# Define the Pydantic model for schema information of a single column
class SchemaInfo(BaseModel):
   """Structure ouput for schema info"""
   column_name: str = Field(description="The name of the column.")
   data_type: str = Field(description="The data type of the column (e.g., string, integer, float, boolean, date).")
   nullable: bool = Field(description="Indicates if the column can contain null values.")
   is_primary: bool = Field(description="Indicates if the column is a primary key.")
   is_foreign_key: bool = Field(description="Indicates if the column is a foreign key.")
   description: str = Field(description="description columns.")
