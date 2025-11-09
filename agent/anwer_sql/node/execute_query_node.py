from agent.anwer_sql.entities.agent_state import AgentState
from db.duckdb import execute_duckdb_query
def execute_query_node(state: AgentState) -> AgentState:
    """Node 2: Execute the generated SQL query"""

    latest_sql = state["sql_queries"][-1]

    result = execute_duckdb_query(latest_sql.sql, latest_sql.tables)

    return {
        "query_results": [result]
    }