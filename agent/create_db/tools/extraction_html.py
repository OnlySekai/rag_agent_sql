from bs4 import BeautifulSoup
from typing import List, Tuple

def extract_sample_table(html_table: str, num_rows: int = 2) -> str:
    """
    Extract a sample table containing the table header and the first num_rows rows.
    
    Args:
        html_table (str): The HTML table as a string.
        num_rows (int): Number of data rows to include (default: 2).
    
    Returns:
        str: The HTML string of the sample table.
    """
    soup = BeautifulSoup(html_table, "html.parser")
    table = soup.find("table")
    if not table:
        raise ValueError("No <table> found in input HTML.")

    # Clone structure for the new sample table
    sample_table = soup.new_tag("table")

    # Copy header if exists
    thead = table.find("thead")
    if thead:
        sample_table.append(thead)

    # Copy first num_rows from tbody or direct tr
    tbody = table.find("tbody")
    rows = []
    if tbody:
        rows = tbody.find_all("tr", recursive=False)[:num_rows]
    else:
        rows = table.find_all("tr", recursive=False)[1:num_rows+1]  # skip header row

    new_tbody = soup.new_tag("tbody")
    for row in rows:
        new_tbody.append(row)
    sample_table.append(new_tbody)

    return str(sample_table)

def extract_table_headers(html: str, return_str: bool = False) -> List[str]:
    """
    Extract all header texts (<th>) from a given HTML table string.
    Returns a list of header names (text only).
    """

    soup = BeautifulSoup(html, "html.parser")
    headers = []

    # Find the first <table>
    table = soup.find("table")
    if not table:
        return headers

    # Find all header cells in the table
    for th in table.find_all("th"):
        text = th.get_text(strip=True)
        if text:
            headers.append(text)
    if return_str:
        return " | ".join(headers)
    return headers

def flatten_html_table(html: str, return_str: bool=False) -> Tuple[List[str], List[List[str]]]:
    """
    Parse and flatten an HTML table.
    Returns:
        headers: list of header names
        rows: list of flattened row lists
    """
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table")
    if not table:
        raise ValueError("No <table> found in HTML")

    headers = []
    rows = []

    for tr in table.find_all("tr"):
        cells = tr.find_all(["th", "td"])
        if not cells:
            continue

        # If contains any <th> → treat as header row
        if tr.find("th"):
            headers = [cell.get_text(strip=True) for cell in cells]
        else:
            row = [cell.get_text(strip=True) for cell in cells]
            rows.append(row)

    if return_str:
        final_str = ""
        final_str += " | ".join(headers) + "\n"
        for row in rows:
            final_str += " ".join(row) + "\n"

    return {"headers": headers, "rows": rows} if not return_str else final_str

def is_simple_table(html: str) -> bool:
    """
    Check if an HTML table is 'simple' — i.e. it has no rowspan or colspan > 1.

    Args:
        html (str): HTML content containing a <table> element.

    Returns:
        bool: True if the table is simple, False otherwise.
    """
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table")
    if not table:
        raise ValueError("No <table> element found in the HTML.")
    
    # Check all table cells
    for cell in table.find_all(["td", "th"]):
        rowspan = int(cell.get("rowspan", "1"))
        colspan = int(cell.get("colspan", "1"))
        if rowspan > 1 or colspan > 1:
            return False
    return True

def remove_auto_index_column(html):
    soup = BeautifulSoup(html, "html.parser")

    for table in soup.find_all("table"):
        rows = table.find_all("tr")
        if not rows:
            continue

        # Try to get the first header text (if available)
        first_header_cell = rows[0].find(["th", "td"])
        header_text = first_header_cell.get_text(strip=True).lower() if first_header_cell else ""

        # Try to get the first data cell in the next row
        first_data_cell = None
        for tr in rows[1:]:
            first_data_cell = tr.find(["td", "th"])
            if first_data_cell:
                break

        first_data_text = first_data_cell.get_text(strip=True) if first_data_cell else ""

        # Check if it’s an integer
        def is_integer(value):
            try:
                int(value)
                return True
            except ValueError:
                return False

        # Determine whether to remove first column
        should_remove = (
            header_text in ["stt", "tt", 'số tt'] or
            is_integer(first_data_text)
        )

        if should_remove:
            for tr in rows:
                first_cell = tr.find(["th", "td"])
                if first_cell:
                    first_cell.decompose()

    return str(soup)

def extract_flatten_table_column(html):
    soup = BeautifulSoup(html, "html.parser")
    thead = soup.find("thead")
    if not thead:
        return []
    rows = thead.find_all("tr")

    # Step 1: Build a 2D header grid
    grid = []
    max_cols = 0
    for row in rows:
        cells = []
        for cell in row.find_all(["th", "td"]):
            rowspan = int(cell.get("rowspan", 1))
            colspan = int(cell.get("colspan", 1))
            cells.append((cell.get_text(strip=True), rowspan, colspan))
        grid.append(cells)
        max_cols = max(max_cols, sum(c[2] for c in cells))

    # Step 2: Build header matrix (fill with None first)
    header_matrix = [[None for _ in range(max_cols)] for _ in range(len(rows))]
    col_tracker = [0] * len(rows)

    for r, row in enumerate(grid):
        c_idx = 0
        for text, rowspan, colspan in row:
            # Find next available column
            while c_idx < max_cols and header_matrix[r][c_idx] is not None:
                c_idx += 1
            for i in range(rowspan):
                for j in range(colspan):
                    header_matrix[r + i][c_idx + j] = text
            c_idx += colspan

    # Step 3: Combine headers vertically
    final_headers = []
    for col in range(max_cols):
        parts = [header_matrix[r][col] for r in range(len(rows)) if header_matrix[r][col]]
        header_name = " ".join(dict.fromkeys(parts))  # remove duplicates, preserve order
        final_headers.append(header_name)

    return final_headers

def extract_table_cells(html):
    """
    Extract non-header cell data from HTML table(s).
    Each cell is represented as:
    {
        "start_row": int,
        "end_row": int,
        "start_column": int,
        "end_column": int,
        "value": str
    }
    Skips only header rows in <thead>.
    """
    soup = BeautifulSoup(html, "html.parser")
    results = []

    for table in soup.find_all("table"):
        # Split rows into header (<thead>) and body (<tbody>)
        thead = table.find("thead")
        tbody = table.find("tbody")

        header_rows = thead.find_all("tr") if thead else []
        body_rows = tbody.find_all("tr") if tbody else table.find_all("tr")

        # Track cell occupancy for rowspan/colspan
        grid = {}
        for r_idx, row in enumerate(body_rows):
            col_idx = 0
            for cell in row.find_all(["td", "th"]):
                # Skip columns already filled by rowspan
                while (r_idx, col_idx) in grid:
                    col_idx += 1

                rowspan = int(cell.get("rowspan", 1))
                colspan = int(cell.get("colspan", 1))

                # Mark grid positions covered by this cell
                for dr in range(rowspan):
                    for dc in range(colspan):
                        grid[(r_idx + dr, col_idx + dc)] = True

                value = cell.get_text(strip=True)
                results.append({
                    "start_row": r_idx,
                    "end_row": r_idx + rowspan - 1,
                    "start_column": col_idx,
                    "end_column": col_idx + colspan - 1,
                    "value": value,
                })
                col_idx += colspan

    return results
