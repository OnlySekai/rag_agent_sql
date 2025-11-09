from langchain_core.prompts import ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from llm.openai_api import llm
from typing import List

class AmbigousDefine(BaseModel):
    """
    Represents a list of ambiguous terms, each with a corresponding definition question.
    """
    ambiguous_terms: List[str] = Field(
        ..., 
        description="A list of ambiguous terms found in the user's question."
    )
    define_questions: List[str] = Field(
        ..., 
        description="A list of questions to ask the user to clarify the definition of each ambiguous term."
    )

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
            You are a helpful assistant that detects ambiguous terms in a user's question and generates questions to clarify their definitions.
            Analyze the user's question and identify any terms that could have multiple meanings or are not specific enough.
            For each ambiguous term, generate a question that asks the user to define the term in the context of their question.
            Return the ambiguous terms and the definition questions as a JSON object.
            """,
        ),
        ("human", "Question: {question}"),
    ]
)

detect_ambiguous_chain = prompt | llm.with_structured_output(AmbigousDefine)

if __name__ == "__main__":
    question = "What is the average score of students in the last semester?"
    result = detect_ambiguous_chain.invoke({"question": question})
    print(result)
