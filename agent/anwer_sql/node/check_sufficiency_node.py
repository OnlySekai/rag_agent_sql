
from agent.anwer_sql.entities.agent_state import AgentState
from agent.anwer_sql.entities.sufficiency_check import SufficiencyCheck
from llm.openai_api import llm_with_temp

from langchain_core.messages import HumanMessage, SystemMessage

def check_sufficiency_node(state: AgentState) -> AgentState:
    """Node 3: Check whether the collected data is sufficient"""

    llm = llm_with_temp(0.0)
    structured_llm = llm.with_structured_output(SufficiencyCheck)

    # Build summary of successful queries only
    successful_data_summary = ""
    
    if state.get("sql_queries") and state.get("query_results"):
        for i, (query_output, result) in enumerate(zip(state["sql_queries"], state["query_results"]), 1):
            if result.get("success"):
                successful_data_summary += f"\n--- Successful Query {i} ---\n"
                # successful_data_summary += f"sql: {query_output.sql}\n"
                # successful_data_summary += f"Knowledge: {query_output.knowledge_summary}\n"
                successful_data_summary += f"Answer: {result.get('answer')}\n"
                # successful_data_summary += f"Data: {result['data']}\n"  # Show more samples

    # # Build available tables context
    available_tables = state.get("table_context")
    system_prompt =  """Analyze whether the collected data is sufficient to answer the question.

Respond strictly in JSON format:
{
    "has_enough_data": true/false,
    "reasoning": "Why it is sufficient or what is missing",
    "missing_info": "Describe missing data if any"
}
If can't get anymore data from {available_tables}, you can set has_enough_data is True.
"""

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"""Question: {state['question']}

Successfully collected data:
{successful_data_summary if successful_data_summary else "No successful queries yet"}

Iteration count: {state.get('iteration_count', 0)}

Analyze the sufficiency and determine next steps.""")
    ]

    response: SufficiencyCheck = structured_llm.invoke(messages)

    print(response)
    return {
        "has_enough_data": response.has_enough_data,  # True means stop iteration
        "messages": [response],
        "final_answer": response.final_answer}