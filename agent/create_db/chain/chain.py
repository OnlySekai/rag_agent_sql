import os
from langchain_core.runnables import RunnableLambda
from agent.create_db.promt.parse_csv import parse_csv_promt
from agent.create_db.entities.table_info import TableOutput
from db.csv import parse_and_save_csv, save_metadata
from llm.openai_api import llm_with_temp

llm = llm_with_temp(1.2).with_structured_output(TableOutput)

def wrapper_save_csv(input: TableOutput):
    name, path = parse_and_save_csv(input.csv_content, input.table_name)
    table_info = input
    table_info.path = path
    table_info.table_name = name
    return table_info


# Define the processing chain
markdown_processor_chain = (
      RunnableLambda(lambda x: {
        "table": x["table"].lower(),
        "src_input": x["src_input"]
    })
    | parse_csv_promt
    | llm
    | wrapper_save_csv
    | save_metadata
    
)