import duckdb

def execute_duckdb_query(sql: str, csv_paths: dict) -> dict:
    """
    Tool to execute SQL queries on DuckDB.

    Args:
        sql: SQL query string
        csv_paths: Dictionary mapping table_name -> CSV file path

    Returns:
        A dictionary containing success status, data, and other info.
    """
    try:
        conn = duckdb.connect(':memory:')

        # Load CSV files
        for table_name, path in csv_paths.items():
            conn.execute(f"CREATE TABLE {table_name} AS SELECT * FROM read_csv_auto('{path}')")

        # Execute query
        result = conn.execute(sql).fetchall()
        columns = [desc[0] for desc in conn.description]

        # Convert to list of dicts
        result_dicts = [dict(zip(columns, row)) for row in result]

        conn.close()

        return {
            "success": True,
            "data": result_dicts,
            "row_count": len(result_dicts),
            "sql": sql
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "sql": sql
        }