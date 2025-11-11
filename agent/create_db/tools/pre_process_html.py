import re
from typing import List
from agent.create_db.tools.extraction_html import *
from langchain_core.messages import HumanMessage, SystemMessage
def replace_br_in_table_cells(html: str, separator: str = " ") -> str:
    """
    Replace all <br> tags inside <td> or <th> cells with a given separator.
    Example: separator=' ' will join lines with a space.
    """
    soup = BeautifulSoup(html, "html.parser")

    # Iterate through all table cells
    for cell in soup.find_all(["td", "th"]):
        # Find all <br> tags in this cell
        for br in cell.find_all("br"):
            # Replace <br> with a separator string node
            br.replace_with(separator)

    return str(soup)

def flatten_paragraph_table(html_table: str) -> List[str]:
    html_table = clean_html_table(html_table)
    # Remove first column if header is 'STT' or 'TT'
    html_table = remove_auto_index_column(html_table)
    # flatten columns if necessary
    # columns = extract_flat_table_column(html_table)
    # extract content cell
    cells = extract_table_cells(html_table)
    # Extract each row
    max_row = max(cell['end_row'] for cell in cells)
    max_col = max(cell['end_column'] for cell in cells)
    cell_matrix = [["" for _ in range(max_col + 1)] for _ in range(max_row + 1)]
    min_row = min(cell['start_row'] for cell in cells)
    for i, cell in enumerate(cells):
        for r in range(cell['start_row'], cell['end_row'] + 1):
            for c in range(cell['start_column'], cell['end_column'] + 1):
                cell_matrix[r][c] = i

    visited = set()
    column_current_unvisited_row = [min_row for _ in range(max_col + 1)]
    content = []
    cur_col = 0
    cell_stack = []
    for i in range(min_row, max_row + 1):
        if cell_matrix[i][cur_col] != "" and cell_matrix[i][cur_col] not in visited:
            cell_stack.append((i, cur_col))
            visited.add(cell_matrix[i][cur_col])
    cell_stack = cell_stack[::-1]
    column_current_unvisited_row[0] = max_row + 1
    while len(cell_stack) > 0:
        r, c = cell_stack.pop()
        cell_id = cell_matrix[r][c]
        cell = cells[cell_id]
        content.append(cell['value'])
        cur_cell_end_row = cell['end_row']
        if cell['end_column'] + 1 <= max_col:
            next_col = cell['end_column'] + 1
            while next_col <= max_col:
                next_cells = []
                for r in range(column_current_unvisited_row[next_col], cur_cell_end_row+1):
                    if cell_matrix[r][next_col] != "" and cell_matrix[r][next_col] not in visited:
                        next_cells.append((r, next_col))
                        visited.add(cell_matrix[r][next_col])

                if len(next_cells) > 0:
                    column_current_unvisited_row[next_col] = cur_cell_end_row + 1
                    for nc in next_cells[::-1]:
                        cell_stack.append(nc)
                    break
                else:
                    next_col += 1
    return '\n'.join(content)

def clean_html_table(html):
    html = replace_br_in_table_cells(html, separator=" ")
    soup = BeautifulSoup(html, "html.parser")

    # Get text and normalize spaces
    cleaned_html = str(soup)
    cleaned_html = re.sub(r'\s+', ' ', cleaned_html).strip()

    return cleaned_html


def extract_table_rows(html_table):
    html_table = clean_html_table(html_table)
    html_table = remove_auto_index_column(html_table)
    columns = extract_flatten_table_column(html_table)
    cells = extract_table_cells(html_table)
    max_row = max(cell['end_row'] for cell in cells)
    max_col = max(cell['end_column'] for cell in cells)
    min_row = min(cell['start_row'] for cell in cells)
    
    # Build cell matrix
    cell_matrix = [["" for _ in range(max_col + 1)] for _ in range(max_row + 1)]
    for cell in cells:
        for r in range(cell['start_row'], cell['end_row'] + 1):
            for c in range(cell['start_column'], cell['end_column'] + 1):
                cell_matrix[r][c] = cell['value'].strip()

    # Build table rows
    table_rows = []
    for r in range(min_row, max_row + 1):
        row_data = {}
        for c in range(max_col + 1):
            if c < len(columns):
                k = columns[c]
            else:
                columns.append(f"column_{c}")
                k = columns[c]
            row_data[k] = cell_matrix[r][c]
        table_rows.append(row_data)

    # Merge empty first-column rows sequentially
    new_table_rows = []
    first_col_name = columns[0] if len(columns) > 0 else "column_0"

    for row in table_rows:
        if not row[first_col_name]:  # Current row first cell is empty
            if new_table_rows:
                prev_row = new_table_rows.pop()
                merged_row = {}
                for k in set(prev_row.keys()).union(row.keys()):
                    merged_row[k] = (prev_row.get(k, "") + " " + row.get(k, "")).strip()
                new_table_rows.append(merged_row)
            else:
                new_table_rows.append(row)
        else:
            new_table_rows.append(row)


    return {"headers": columns, "rows": new_table_rows}

def convert_first_table_row_to_headers(html_table: str) -> str:
    soup = BeautifulSoup(html_table, "html.parser")
    table = soup.find("table")
    if not table:
        return html_table  # Not a table, return as-is

    # Check if table already has <th>
    if table.find("th"):
        return html_table  # Already has header, do nothing

    rows = table.find_all("tr")
    if not rows:
        return html_table  # No rows, return as-is

    # Get max columns in table
    max_cols = 0
    for row in rows:
        col_count = sum(int(cell.get("colspan", 1)) for cell in row.find_all(["td", "th"]))
        max_cols = max(max_cols, col_count)

    # Determine first rows: number of rows spanned by first row's cells
    first_row = rows[0]
    first_row_span = max(int(cell.get("rowspan", 1)) for cell in first_row.find_all(["td", "th"]))

    # Check if these first rows have max columns
    correct_first_rows = []
    for i in range(first_row_span):
        if i < len(rows):
            row = rows[i]
            correct_first_rows.append(row)

    # Convert these rows to header rows
    for row in correct_first_rows:
        for cell in row.find_all("td"):
            cell.name = "th"

    return str(soup)

def correct_first_table_row(html_table: str, to_header: bool):
    table = BeautifulSoup(html_table, "html.parser").find("table")
    rows = table.find_all("tr")
    if not rows:
        return html_table  # No rows, return as-is
    first_row = rows[0]
    if not first_row:
        return html_table
    first_row_span = max(int(cell.get("rowspan", 1)) for cell in first_row.find_all(["td", "th"]))
    # Check if these first rows have max columns
    correct_first_rows = []
    for i in range(first_row_span):
        if i < len(rows):
            row = rows[i]
            correct_first_rows.append(row)
    # Convert these rows to header rows or data rows
    if to_header:
        for row in correct_first_rows:
            for cell in row.find_all("td"):
                cell.name = "th"
    else:
        for row in correct_first_rows:
            for cell in row.find_all("th"):
                cell.name = "td"
    return str(table)

def is_first_table_row_headers(html_table: str):
    system_promt = SystemMessage(content="""
         Bạn là một trợ lý AI thông minh. Hãy cho biết hàng đầu tiên của bảng HTML sau đây có chứa tên cột bảng không. 
         Trả lời "Có" hoặc "Không". Không cần giải thích thêm.
         Lưu ý: Do bảng có thể bị lỗi định dạng nên có thể hàng đầu tiên không được đánh dấu là tiêu đề (thẻ <th>), nhưng nó vẫn có thể chứa tên cột. Do đó dựa vào ngữ nghĩa của hàng đầu tiên để trả lời.
        """)
    human_promt = HumanMessage(content="""Bảng HTML: {table_html}""")
    from llm.openai_api import llm_with_temp
    llm = llm_with_temp(1.2)
    response = llm.invoke([system_promt,human_promt])
    response = response.strip().lower()
    if "có" in response:
        return True
    return False

def process_html_table(table_html: str) -> str:
    """
    Example table processor — modify this function for your use case.
    Currently, it uppercases all text inside the table.
    """
    soup = BeautifulSoup(table_html, "html.parser")
    for td in soup.find_all(["td", "th"]):
        if td.string:
            td.string = td.string.upper()
    return str(soup)


def process_tables_in_markdown(md_text: str, process_fn) -> str:
    """
    Extracts all <table> elements from a markdown string,
    applies process_fn(table_html) -> new_table_html,
    and replaces the old tables with the new ones.
    """
    soup = BeautifulSoup(md_text, "html.parser")

    # Iterate over each <table> and replace it with processed one
    for table in soup.find_all("table"):
        old_html = str(table)
        new_html = process_fn(old_html)

        # Replace using BeautifulSoup replace_with to preserve structure
        new_table = BeautifulSoup(new_html, "html.parser")
        table.replace_with(new_table)

    # Return the modified markdown string
    return str(soup)


def process_html_table(table_html: str) -> str:
    """
    Example table processor — modify this function for your use case.
    Currently, it uppercases all text inside the table.
    """
    soup = BeautifulSoup(table_html, "html.parser")
    for td in soup.find_all(["td", "th"]):
        if td.string:
            td.string = td.string.upper()
    return str(soup)


def correct_table_header_markdown(md_text: str) -> str:
    """
    Extracts all <table> elements from a markdown string,
    applies process_fn(table_html) -> new_table_html,
    and replaces the old tables with the new ones.
    """
    soup = BeautifulSoup(md_text, "html.parser")

    # Iterate over each <table> and replace it with processed one
    for table in soup.find_all("table"):
        table_html = str(table)

        sample_table = extract_sample_table(table_html, num_rows=4)
        should_correct = is_first_table_row_headers(sample_table)
        if should_correct:
            new_html = convert_first_table_row_to_headers(table_html)
        else:
            new_html = convert_first_table_row_to_headers(table_html, to_header=False)

        # Replace using BeautifulSoup replace_with to preserve structure
        new_table = BeautifulSoup(new_html, "html.parser")
        table.replace_with(new_table)

    # Return the modified markdown string
    return str(soup)
