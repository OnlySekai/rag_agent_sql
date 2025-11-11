from concurrent.futures import ProcessPoolExecutor

def _process_single_table(table_html: str) -> str:
    """
    Worker function that processes one table.
    Adjust logic here as needed.
    """
    sample_table = extract_sample_table(table_html, num_rows=4)
    should_correct = is_first_table_row_headers(sample_table)
    if should_correct:
        new_html = correct_first_table_row(table_html, to_header=True)
    else:
        new_html = correct_first_table_row(table_html, to_header=False)
    return new_html

def correct_table_header_markdown_parallel(md_text: str, max_workers: int = 4) -> str:
    """
    Extracts all <table> elements from a markdown string,
    processes them in parallel, and replaces them with corrected ones.
    """

    soup = BeautifulSoup(md_text, "html.parser")
    tables = soup.find_all("table")

    if not tables:
        return md_text

    # Step 1: Extract HTML strings
    table_htmls = [str(t) for t in tables]

    # Step 2: Process in parallel
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(_process_single_table, table_htmls))

    # Step 3: Replace each table with its processed version
    for table, new_html in zip(tables, results):
        new_table = BeautifulSoup(new_html, "html.parser")
        table.replace_with(new_table)

    # Step 4: Return the reconstructed markdown
    return str(soup)

def normalize_table_header_row(table_html: str) -> str:
    """
    Convert all <td> cells inside <thead> to <th> tags.
    """
    soup = BeautifulSoup(table_html, "html.parser")

    # Find all <thead> sections in the table
    for thead in soup.find_all("thead"):
        for cell in thead.find_all("td"):
            cell.name = "th"

    return str(soup)

def first_table_row_has_empty_cell(table_html: str) -> bool:
    """
    Check if the first row (<tr>) of a table has any empty cell (<td> or <th>).
    Returns True if at least one cell is empty, else False.
    """
    soup = BeautifulSoup(table_html, "html.parser")
    table = soup.find("table")
    if not table:
        return False  # Not a valid table

    first_row = table.find("tr")
    if not first_row:
        return False  # No rows found

    for cell in first_row.find_all(["td", "th"]):
        # Check if cell text (after stripping) is empty
        if not cell.get_text(strip=True):
            return True

    return False

def normalize_table_header_markdown(md_text: str) -> str:
    """
    Normalize all tables in markdown by converting <td> in <thead> to <th>.
    """
    def process_fn(table_html: str) -> str:
        table_html = normalize_table_header_row(table_html)
        if first_table_row_has_empty_cell(table_html):
            table_html = correct_first_table_row(table_html, to_header=False)
        return table_html

    return process_tables_in_markdown(md_text, process_fn)

def normalize_table_cell_markdown(md_text):
    """
    Normalize all tables in markdown by replacing <br> in cells with spaces.
    """
    def process_fn(table_html: str) -> str:
        return replace_br_in_table_cells(table_html, separator=" ")

    return process_tables_in_markdown(md_text, process_fn)