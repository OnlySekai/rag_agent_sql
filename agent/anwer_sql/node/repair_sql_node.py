from agent.anwer_sql.entities.agent_state import AgentState
from agent.anwer_sql.entities.sql_output import  SQLQueryOutput
from llm.openai_api import llm_with_temp

from langchain_core.messages import HumanMessage, SystemMessage


def repair_sql_node(state: AgentState) -> AgentState:
    """Attempt to fix SQL errors based on DuckDB error messages."""

    last_result = state["query_results"][-1]

    # Only repair if the last query failed
    if last_result.get("success", True):
        return {}

    error_msg = last_result.get("error", "")
    failed_query = state["sql_queries"][-1]  # Get the full SQLQueryOutput object
    failed_sql = failed_query.sql

    llm = llm_with_temp(0)
    
    # Use structured output
    structured_llm = llm.with_structured_output(SQLQueryOutput)

    # Build available tables info
    tables_info = state.get("table_context")

    system_prompt = f"""You are an SQL repair assistant for DuckDB.
Given a failed SQL query and the error message, generate a corrected SQL query.

Available tables with paths:
{tables_info}

Rules:
- Keep the original intent and knowledge goal of the query
- Fix syntax errors, typos, or incorrect table/column names
- Use valid DuckDB syntax
- Ensure table names and paths are correct
- If the error indicates missing columns, adjust the SELECT clause

Return:
1. sql: The corrected SQL query
2. tables: Dictionary mapping table names to their paths (same as original or corrected)
3. knowledge_summary: Same knowledge goal as the original query"""

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"""Original SQL Query:
{failed_sql}

Original Knowledge Goal:
{failed_query.knowledge_summary}

Original Tables Used:
{failed_query.tables}

Error Message:
{error_msg}

Generate the corrected SQL query with proper structure:""")
    ]

    response: SQLQueryOutput = structured_llm.invoke(messages)

    return {
        "sql_queries": [response],  # Add corrected SQLQueryOutput
        "messages": [HumanMessage(content=f"""🔧 SQL Repair Attempted:
Original: {failed_sql}
Error: {error_msg}
Fixed: {response.sql}
Knowledge Goal: {response.knowledge_summary}""")]
    }