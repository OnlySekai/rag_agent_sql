from agent.anwer_sql.graph import create_agent_graph
from agent.anwer_sql.entities.agent_state import AgentState
# ============= MAIN EXECUTION =============
def run_agent(table_context: str, question: str):
    """Run the agent for a given question"""

    app = create_agent_graph()

    initial_state = {
        "table_context": table_context,
        "question": question,
        "sql_queries": [],
        "query_results": [],
        "messages": [],
        "has_enough_data": False,
        "knowledge_answers": "",
        "final_answer": "",
        "iteration_count": 0,

    }

    final_state = app.invoke(initial_state)

    return final_state

def get_final_and_support_data(state: AgentState):
    knowledge_answers = []
    for i, (query_output, result) in enumerate(zip(state["sql_queries"], state["query_results"]), 1):
        if result.get("success"):
            knowledge_answers.append((query_output.knowledge_summary, result['anwser']))
    return {
        "final_answer": state['final_answer'],
        "knowledge_answers": knowledge_answers
    }

def trace(result: AgentState):
    print("====== ASWER =====")
    print(get_final_and_support_data(result))
    print("\n=== PROCESS ===")
    print(result['ambiguous_terms'])
    for i, (sql, sql_rs) in enumerate(zip(result["sql_queries"], result["query_results"]), 1):
        print("Knowleade: ", sql.knowledge_summary)
        print(f"Query {i}:")
        print(sql.sql)
        print(sql_rs)
        print("------------------")