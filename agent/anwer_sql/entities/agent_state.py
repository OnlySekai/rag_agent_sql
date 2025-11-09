from agent.create_db.entities.table_info import TableOutput
from agent.anwer_sql.entities.sql_output import SQLQueryOutput
from typing import TypedDict, Annotated, List
import operator

class AgentState(TypedDict):
    """Defines the agent state"""
    table_context: str
    question: str  # Original user question
    sql_queries: Annotated[List[SQLQueryOutput], operator.add]  # List of SQL queries with table paths
    query_results: Annotated[List[dict], operator.add]  # Query results
    messages: Annotated[List, operator.add]  # Conversation history
    has_enough_data: bool  # Whether we have sufficient data to answer
    final_answer: str  # Final generated answer
    knowledge_answers: str 
    iteration_count: int  # To prevent infinite loops