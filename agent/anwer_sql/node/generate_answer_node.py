
from agent.anwer_sql.entities.agent_state import AgentState
from llm.openai_api import llm_with_temp
from agent.anwer_sql.entities.answer import KnowledgeAnswer, FinalAnswerOutput
from langchain_core.messages import HumanMessage, SystemMessage





def generate_answer_node(state: AgentState) -> AgentState:
    """Node 4: Generate the final answer with reasoning based on all collected data"""

    llm = llm_with_temp(0)
    structured_llm = llm.with_structured_output(FinalAnswerOutput)

    # Build complete data context from successful queries
    data_context = ""
    for i, (query_output, result) in enumerate(zip(state["sql_queries"], state["query_results"]), 1):
        if result.get("success"):
            data_context += f"\n{'='*70}\n"
            data_context += f"Query {i}\n"
            data_context += f"{'='*70}\n"
            data_context += f"Knowledge Goal: {query_output.knowledge_summary}\n"
            data_context += f"SQL: {query_output.sql}\n"
            data_context += f"\nResults ({result.get('row_count', 0)} rows):\n"
            data = result.get('data', [])
            data_context += f"{data}\n\n"

    system_prompt = """You are a data analyst providing a comprehensive answer based on collected data.

Your task:
1. Analyze all the data provided from each query
2. Answer each knowledge question using the actual data
3
. Synthesize a final, complete answer to the user's original question

Requirements:
- Analyze the actual data carefully - look for patterns, trends, outliers
- Be specific and cite concrete data points (actual values, counts, etc.)
- Ensure the final answer directly addresses the original question
- Use statistics where appropriate (averages, totals, percentages, etc.)
- If data is insufficient for a complete answer, acknowledge what's missing"""

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"""Original Question: {state['question']}

All Collected Data:
{data_context}

Please analyze this data and provide:
1. Answer each knowledge question by analyzing its corresponding data
2. Show your reasoning process
3. Provide a final comprehensive answer to the original question""")
    ]

    response: FinalAnswerOutput = structured_llm.invoke(messages)

    # Format the complete answer for display
    formatted_output = "📊 ANALYSIS RESULTS\n\n"
    
    # Section 1: Knowledge Answers
    formatted_output += "=" * 70 + "\n"
    formatted_output += "KNOWLEDGE QUESTIONS & ANSWERS\n"
    formatted_output += "=" * 70 + "\n\n"
    
    for i, ka in enumerate(response.knowledge_answers, 1):
        formatted_output += f"{i}. {ka.knowledge_question}\n"
        formatted_output += f"   Answer: {ka.answer}\n"
        formatted_output += f"   Supporting Data: {ka.supporting_data}\n\n"
    
    # Section 3: Final Answer
    formatted_output += "=" * 70 + "\n"
    formatted_output += "FINAL ANSWER\n"
    formatted_output += "=" * 70 + "\n"
    formatted_output += f"{response.final_answer}\n"

    return {
        "final_answer": response.final_answer,
        "knowledge_answers": [i.json() for i in response.knowledge_answers],
        "messages": [HumanMessage(content=formatted_output)]
    }