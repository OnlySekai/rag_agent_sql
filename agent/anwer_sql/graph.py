from agent.anwer_sql.entities.agent_state import AgentState
from langgraph.graph import StateGraph, END
from agent.anwer_sql.node.gen_sql import generate_sql_node
from agent.anwer_sql.node.execute_query_node import execute_query_node
from agent.anwer_sql.node.repair_sql_node import repair_sql_node
from agent.anwer_sql.node.check_sufficiency_node import check_sufficiency_node
from agent.anwer_sql.node.generate_answer_node import generate_answer_node
# ============= ROUTING LOGIC =============
def should_continue(state: AgentState) -> str:
    """Decide whether to continue querying or generate the final answer"""

    if state.get("iteration_count", 0) >= 5:
        return "generate_answer"

    if not state.get("query_results"):
        return "execute_query"

    if state.get("has_enough_data"):
        return "generate_answer"
    else:
        return "generate_sql"
    
def create_agent_graph():
    """Builds the LangGraph workflow with self-repairing SQL logic."""

    workflow = StateGraph(AgentState)

    # === Define all nodes ===
    workflow.add_node("generate_sql", generate_sql_node)
    workflow.add_node("execute_query", execute_query_node)
    workflow.add_node("repair_sql", repair_sql_node)
    workflow.add_node("check_sufficiency", check_sufficiency_node)
    workflow.add_node("generate_answer", generate_answer_node)

    # === Entry point ===
    workflow.set_entry_point("generate_sql")

    # === Main edges ===
    workflow.add_edge("generate_sql", "execute_query")

    # Conditional edge after executing query
    workflow.add_conditional_edges(
        "execute_query",
        # Decide what to do based on success/failure
        lambda state: (
            "repair_sql"
            if not state["query_results"][-1].get("success", True)
            else "check_sufficiency"
        ),
        {
            "repair_sql": "repair_sql",
            "check_sufficiency": "check_sufficiency",
        },
    )

    # After repairing SQL, re-run the query
    workflow.add_edge("repair_sql", "execute_query")

    # Conditional logic after sufficiency check
    workflow.add_conditional_edges(
        "check_sufficiency",
        should_continue,
        {
            "generate_sql": "generate_sql",
            "generate_answer": "generate_answer",
            "execute_query": "execute_query",
        },
    )

    # End of graph
    workflow.add_edge("generate_answer", END)

    # Compile graph to runnable form
    return workflow.compile()
