from agent.anwer_sql.graph import create_agent_graph
from agent.anwer_sql.entities.agent_state import AgentState
# ============= MAIN EXECUTION =============
import signal

class TimeoutError(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutError("Agent execution exceeded 90 seconds")

def run_agent(table_context: str, question: str, timeout_seconds: int = 90):
    """Run the agent for a given question with timeout"""
    
    # Set up the timeout
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(timeout_seconds)
    
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
        
        # Cancel the alarm
    signal.alarm(0)
        
    return final_state

def get_final_and_support_data(state: AgentState):
    knowledge_answers = []
    for i, (query_output, result) in enumerate(zip(state["sql_queries"], state["query_results"]), 1):
        if result.get("success"):
            knowledge_answers.append((query_output.knowledge_summary, result.get('anwser', "")))
    return {
        "final_answer": state['final_answer'],
        "knowledge_answers": knowledge_answers
    }

def predict(table_context: str, question: str, timeout_seconds: int = 90):
    try:
        state = run_agent(table_context, question, timeout_seconds)
        return get_final_and_support_data(state)
    except Exception as e:
        print(f"❌ Error in predict: {e}")
        return {
            "final_answer": "",
            "knowledge_answers": ""
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