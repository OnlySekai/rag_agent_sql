
from agent.anwer_sql.entities.agent_state import AgentState
from agent.anwer_sql.entities.sufficiency_check import SufficiencyCheck
from llm.openai_api import llm_with_temp

from langchain_core.messages import HumanMessage, SystemMessage

def check_sufficiency_node(state: AgentState) -> AgentState:
    """Node 3: Check whether the collected data is sufficient"""

    llm = llm_with_temp(0.5)
    structured_llm = llm.with_structured_output(SufficiencyCheck)

    # Build summary of successful queries only
    successful_data_summary = ""
    failed_queries_summary = ""
    
    if state.get("sql_queries") and state.get("query_results"):
        for i, (query_output, result) in enumerate(zip(state["sql_queries"], state["query_results"]), 1):
            if result.get("success"):
                successful_data_summary += f"\n--- Successful Query {i} ---\n"
                successful_data_summary += f"SQL: {query_output.sql}\n"
                successful_data_summary += f"Knowledge: {query_output.knowledge_summary}\n"
                successful_data_summary += f"Rows: {result.get('row_count', 0)}\n"
                successful_data_summary += f"Sample Data: {result['data'][:5]}\n"  # Show more samples

    # Build available tables context
    available_tables = state.get("table_context")
    system_prompt = f"""Analyze whether the collected data is sufficient to answer the user's question completely.

Your task:
1. Determine if current data fully answers the question
2. Identify any missing information needed
3. Check if additional helpful data can be collected from available tables
4. Verify concept clarity and contextual grounding
5. If no more useful data can be collected, recommend stopping

Important rules:
- Set has_enough_data=true only if the question can be answered completely
- Set can_collect_more=false if:
  * All necessary data has been collected, OR
  * No additional queries would provide useful information, OR
  * Further queries would just repeat what we already have
- If can_collect_more=true, provide a clear suggested_next_query description

Contextual Grounding:
- Verify all references are backed by retrieved data, not assumptions:
  * Names, categories, IDs must exist in the data
  * Date ranges should align with available data periods
  * Aggregations should be based on actual column values
- Check if data_lv is being respected:
  * Nominal: Are we treating categories correctly without assuming order?
  * Ordinal: Are we using proper ordering without invalid arithmetic?
  * Interval/Ratio: Are calculations appropriate for the measurement level?
- Confirm any filters or conditions reference actual values from the data

Missing Information Assessment:
- List specific data points still needed (be concrete, not vague)
- For each missing piece, verify it exists in available schemas before suggesting collection
- Consider whether missing information is:
  * Critical: Required to answer the question
  * Supplementary: Would improve answer quality
  * Redundant: Already implied by collected data

Return your analysis with clear reasoning for each decision point.
{available_tables}"""

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"""Question: {state['question']}

Successfully collected data:
{successful_data_summary if successful_data_summary else "No successful queries yet"}

Failed queries:
{failed_queries_summary if failed_queries_summary else "No failed queries"}

Iteration count: {state.get('iteration_count', 0)}

Analyze the sufficiency and determine next steps.""")
    ]

    response: SufficiencyCheck = structured_llm.invoke(messages)

    # Determine if we should continue querying
    # Stop if: has enough data OR cannot collect more useful data
    should_stop = response.has_enough_data or not response.can_collect_more

    return {
        "has_enough_data": should_stop,  # True means stop iteration
        "messages": [response]}