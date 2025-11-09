from agent.anwer_sql.entities.agent_state import AgentState, SQLQueryOutput
from llm.openai_api import llm_with_temp

from langchain_core.messages import HumanMessage, SystemMessage

# ============= NODE FUNCTIONS =============
def generate_sql_node(state: AgentState) -> AgentState:
    """Node 1: Generate SQL query based on question and existing data"""

    llm = llm_with_temp(0)
    
    # Create structured output LLM
    structured_llm = llm.with_structured_output(SQLQueryOutput)

    # Build context from previous queries (only successful ones)
    previous_context = ""
    failed_context = ""
    
    if state.get("sql_queries") and state.get("query_results"):
        successful_queries = []
        failed_queries = []
        
        for i, query_output in enumerate(state["sql_queries"]):
            # Check if corresponding result exists and was successful
            if i < len(state["query_results"]):
                result = state["query_results"][i]
                if result.get("success", False):
                    successful_queries.append((query_output, result))
                else:
                    failed_queries.append((query_output, result))
        
        if successful_queries:
            previous_context = "\n\nPreviously collected data (successful queries only):\n"
            for idx, (query_output, result) in enumerate(successful_queries, 1):
                previous_context += f"\nQuery {idx}: {query_output.sql}\n"
                previous_context += f"Knowledge retrieved: {query_output.knowledge_summary}\n"
                previous_context += f"Tables used: {', '.join(query_output.tables.keys())}\n"
                previous_context += f"Rows: {result.get('row_count', 0)}\n"
                if result.get("data"):
                    previous_context += f"Sample: {result['data'][:3]}\n"
        
        if failed_queries:
            failed_context = "\n\nFailed queries (DO NOT repeat these patterns):\n"
            for idx, (query_output, result) in enumerate(failed_queries, 1):
                failed_context += f"\nFailed Query {idx}: {query_output.sql}\n"
                failed_context += f"Error: {result.get('error', 'Unknown error')}\n"

    # Build available tables info with paths
    tables_info = ""
    table_context = state.get('table_context', [])
    for table_info in table_context:
        table_name = table_info.name if hasattr(table_info, 'name') else str(table_info)
        table_path = table_info.path if hasattr(table_info, 'path') else None
        tables_info += f"\n- Table: {table_name}" + (f" (Path: {table_path})" if table_path else "")

    system_prompt = f"""{state.get('table_context')}

Available tables with paths:
{tables_info}

Task: Generate an SQL query to retrieve the necessary data to answer the question.

Rules:
- Use DuckDB syntax.
- Table names: sales, customers, products.
- If data has been retrieved before, generate additional queries for missing information.
- Never guess missing details (like specific subject names).
- Never include assumptions like "-- Assuming 'English' is the language subject".
- If the question refers to something not specific, then
   - Generate SQL covering all matching necessary data.
   - Think which options will match.
   - Example: the term "language subject", must select all subjects and think which are the "language subject"
{previous_context}
{failed_context}

Return:
1. sql: The SQL query string
2. tables: A dictionary mapping each table name used in the query to its file path
3. knowledge_summary: A brief 1-2 sentence summary explaining what specific information/knowledge this query will retrieve and how it helps answer the user's question"""

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"Question: {state['question']}\n\nGenerate the SQL query with table paths:")
    ]

    # Invoke structured LLM
    response: SQLQueryOutput = structured_llm.invoke(messages)

    return {
        "sql_queries": [response],  # Add SQLQueryOutput object to list
        "messages": [HumanMessage(content=f"Generated SQL: {response.sql}\nKnowledge: {response.knowledge_summary}")],
        "iteration_count": state.get("iteration_count", 0) + 1
    }