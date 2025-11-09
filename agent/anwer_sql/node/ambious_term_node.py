from agent.anwer_sql.entities.agent_state import AgentState
from agent.anwer_sql.entities.sufficiency_check import SufficiencyCheck
from llm.openai_api import llm_with_temp
from agent.anwer_sql.entities.ambious_term import AmbiousTerm
from langchain_core.messages import HumanMessage, SystemMessage

def detect_ambious_term(state: AgentState) -> AgentState:
    llm = llm_with_temp(0.5).with_structured_output(AmbiousTerm)
    system_prompt = """You are a helpful assistant that detects ambiguous terms in a user's question and generates questions to clarify their definitions.
            Analyze the user's question and identify any terms that could have multiple meanings or are not specific enough.
            For each ambiguous term, generate a question that asks the user to define the term in the context of their question.
            Return the ambiguous terms and the definition questions as a JSON object.
            """
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"""Question: {state['question']}""")]

    response: SufficiencyCheck = llm.invoke(messages)
    return {
        "ambiguous_terms": response.definition_questions
        }