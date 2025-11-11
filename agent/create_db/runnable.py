from agent.create_db.chain.chain import raw_markdown_processor_chain, raw_markdown_processor_chain_v2
from agent.create_db.tools.pre_process_html import extract_table_rows
from db.csv import parse_and_save_csv, save_metadata
import pandas as pd

def preprocess_table(html, save_dir):
    input =raw_markdown_processor_chain.invoke({"table": html, "src_input": "html"})
    name, path = parse_and_save_csv(input.csv_content, input.table_name, save_dir)
    table_info = input
    table_info.path = path
    table_info.table_name = name
    metadata_path, metdata = save_metadata(table_info, save_dir)
    return {
        "metadata_path":metadata_path,
        "data_csv_path": path,
        "metadata": metdata
    }
def preprocess_table_v2(html, save_dir):
    rows = extract_table_rows(html.lower())['rows']
    r_df = pd.DataFrame(rows)
    example = r_df.head(20).to_string()
    input =raw_markdown_processor_chain_v2.invoke({"table": example})
    name, path = parse_and_save_csv(r_df, input.table_name, save_dir)
    table_info = input
    table_info.path = path
    table_info.table_name = name
    metadata_path, metdata = save_metadata(table_info, save_dir)
    return {
        "metadata_path":metadata_path,
        "data_csv_path": path,
        "metadata": metdata
    }
    

def is_small_table(html, n_word):
    return len(html) <n_word