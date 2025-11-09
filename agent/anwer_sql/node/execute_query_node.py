from agent.anwer_sql.entities.agent_state import AgentState
from db.duckdb import execute_duckdb_query
from llm.openai_api import llm_with_temp
from langchain_core.messages import HumanMessage, SystemMessage


def execute_query_node(state: AgentState) -> AgentState:
    """Node 2: Execute the generated SQL query and answer the knowledge question with LLM"""

    # Build context from previous successful queries
    previous_context = ""
    if state.get("sql_queries") and state.get("query_results"):
        successful_queries = []
        
        for i, query_output in enumerate(state["sql_queries"]):
            if i < len(state["query_results"]):
                result_old = state["query_results"][i]
                if result_old.get("success", False):
                    successful_queries.append((query_output, result_old))
        
        if successful_queries:
            previous_context = "\n\nPreviously collected knowledge:\n"
            for idx, (query_output, result_old) in enumerate(successful_queries, 1):
                previous_context += f"{idx}. Question: {query_output.knowledge_summary}\n"
                previous_context += f"   Answer: {result_old.get('answer', 'N/A')}\n\n"

    # Get latest SQL query
    latest_sql = state["sql_queries"][-1]

    # Execute the SQL query
    result = execute_duckdb_query(latest_sql.sql, latest_sql.tables)

    # If query failed, return error without LLM analysis
    if not result.get("success"):
        return {
            "query_results": [result]
        }

    llm = llm_with_temp(0.5)

    data = result.get('data', [])
    row_count = result.get('row_count', 0)

    data_for_llm = data
    data_note = ""
    if len(data) > 200:
        data_for_llm = data
        data_note = f"\n(Showing first 100 and last 100 of {len(data)} total rows)"
    system_prompt = f"""You are a data analyst answering specific questions based on SQL query results.

Your task: Answer the knowledge question directly and concisely based on the data.

Guidelines:
- Provide a clear, direct answer
- Be specific with numbers and data points
- Focus on answering the question, not explaining the process
- Use simple, clear language
- Keep answer to 2-3 sentences maximum

{previous_context}

IMPORTANT: Return ONLY the answer text, no formatting, no structure, no labels."""

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"""Knowledge Question: {latest_sql.knowledge_summary}

SQL Query: {latest_sql.sql}

Query Results ({row_count} rows):{data_note}
{data_for_llm}

Answer the knowledge question:""")
    ]

    llm_response = llm.invoke(messages)
    answer_text = llm_response.content.strip()
    
    # Enhance result with LLM answer
    enhanced_result = {
        **result,
        "answer": answer_text
    }
    return {
        "query_results": [enhanced_result]
    }