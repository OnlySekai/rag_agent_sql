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
                # previous_context += f"\nQuery {idx}: {query_output.sql}\n"
                previous_context += f"Knowledge retrieved: {query_output.knowledge_summary}\n"
                previous_context += f"answer: {result.get('answer', 0)}\n"
        
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
- when a column or table name contains spaces or special characters, you must enclose it in double quotes
- Table names: sales, customers, products.
- If data has been retrieved before, generate additional queries for missing information.
- You must resolve all ambiguous term: {state['ambiguous_terms']}
- Never guess missing details (like specific subject names).
- With the term was resolved, you can have many assumtions to collect information
- When must has human's desicion, you will could be continue collect all potential usecase.

Schema Analysis Guidelines:
- Use 'data_lv' to determine appropriate operations:
  * Nominal/Ordinal (is_category=true): Use GROUP BY, COUNT, DISTINCT for aggregations. Use exact matching for filtering.
  * Ordinal: Can use comparison operators (>, <, >=, <=) when order is meaningful (e.g., ratings, levels).
  * Interval/Ratio (is_category=false): Can use arithmetic operations (SUM, AVG, MIN, MAX, mathematical expressions).
- Use 'is_category' to decide:
  * If true: Focus on frequency counts, distributions, groupings, and categorical filtering.
  * If false: Can perform numerical calculations, statistical aggregations, and range queries.
- For categorical columns (is_category=true), always consider retrieving ALL distinct values when the question is ambiguous.
- For ratio-level data, ratios and percentages are meaningful (e.g., "twice as much", "50% more").
- For ordinal data, ordering makes sense but arithmetic operations may not (e.g., "high > medium > low" but not "high + low").
{previous_context}
{failed_context}

Missing information: {state['messages'][-1].missing_info if len(state['messages'])> 0 else "ALL"}
Ressoning: {state['messages'][-1].reasoning if len(state['messages'])> 0 else "NONE"}

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