"""Ambiguity resolution node module for LangGraph orchestration.

This module acts as a gatekeeper before executing high-stakes portfolio 
actions, analyzing if the Relationship Manager's natural language request 
is missing critical operational parameters (e.g., exact asset or amount).
"""

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage
from langchain_groq import ChatGroq
from pydantic import BaseModel, Field
import sys
import os

from shared.security_config import get_groq_api_key
from langgraph_orchestrator.state import AgentState

class ClarificationCheck(BaseModel):
    """Schema defining the structured output for ambiguity detection.
    
    Attributes:
        is_ambiguous: Boolean indicating if the request lacks specific parameters.
        missing_details: A generated follow-up query to extract missing context.
    """
    is_ambiguous: bool = Field(..., description="True if the request is for a trade/reallocation but missing specific amounts or target assets.")
    missing_details: str = Field(..., description="If ambiguous, a friendly question asking the Relationship Manager for the missing details. Empty string if not ambiguous.")

llm = ChatGroq(
    model=os.getenv("GROQ_ROUTER_MODEL", "llama-3.3-70b-versatile"),
    api_key=get_groq_api_key(),
    temperature=0,
)
checker_llm = llm.with_structured_output(ClarificationCheck)

system_prompt = """You are the Ambiguity Checker for Pramiti OS.
Your job is to prevent the Portfolio Agent from generating generic, empty proposals.
If the Relationship Manager (RM) asks to "reallocate some money" or "buy some stock" without specifying WHICH asset or HOW MUCH, you must flag this as ambiguous.
If it is a generic query (e.g. "What is the AUM?"), it is NOT ambiguous.

Evaluate the RM's latest request and return whether it is ambiguous and what is missing.
"""

def ambiguity_node(state: AgentState) -> dict:
    """Evaluates transactional intent for completeness of operational parameters.
    
    Analyzes the latest message from the Relationship Manager. If it implies a 
    portfolio modification but omits specific targets (amount, instrument), it 
    flags the workflow to request clarification instead of progressing.
    
    Args:
        state: The current state of the LangGraph workflow.
        
    Returns:
        dict: A dictionary containing the `requires_clarification` boolean flag 
              and conditionally appended clarification `messages`.
    """
    messages = state.get("messages", [])
    
    raw_content = messages[-1].content
    last_msg = (
        raw_content if isinstance(raw_content, str)
        else " ".join(str(part) for part in raw_content)
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{request}")
    ])
    
    chain = prompt | checker_llm
    
    raw_result = chain.invoke({"request": last_msg})
    
    if isinstance(raw_result, dict):
        result = ClarificationCheck.model_validate(raw_result)
    elif isinstance(raw_result, ClarificationCheck):
        result = raw_result
    else:
        result = ClarificationCheck.model_validate(raw_result.model_dump() if hasattr(raw_result, "model_dump") else raw_result)
    
    if result.is_ambiguous:
        return {
            "requires_clarification": True,
            "messages": [AIMessage(content=f"⚠️ Clarification Needed: {result.missing_details}")]
        }
    else:
        return {
            "requires_clarification": False
        }
