from agent.create_db.chain.chain import raw_markdown_processor_chain
from db.csv import parse_and_save_csv, save_metadata

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


def is_small_table(html, n_word):
    return len(html) <n_word