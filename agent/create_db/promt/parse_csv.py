from langchain_core.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate, ChatPromptTemplate

# Define the system and human prompts
system_prompt = SystemMessagePromptTemplate.from_template(
    "You are a helpful assistant that converts {src_input} tables to CSV, infers schema, and summarizes the content. "
    "Your output should be a JSON object matching the provided schema.",
)

human_prompt = HumanMessagePromptTemplate.from_template(
    """Convert the following {src_input} table to a flattened CSV format.
    Ensure the header row is not duplicated and handle merged cells appropriately.
    Then, provide the inferred schema as a list of dictionaries, where each dictionary represents a column and has keys:
    - 'column_name': The name of the column.
    - 'data_type': The data type of the column (e.g., string, integer, float).
    - 'nullable': Whether the column allows null values (true/false).
    - 'is_primary': Whether the column is a primary key (true/false).
    - 'is_foreign_key': Whether the column is a foreign key (true/false).

    Finally, provide a summary of the table content for retrieval tasks. 
    Ensure that the language of the summary matches the language of the table content.

    {src_input} table:
    {table}
    """,
)

# Combine the prompts into a chat prompt template
parse_csv_promt = ChatPromptTemplate.from_messages([system_prompt, human_prompt])