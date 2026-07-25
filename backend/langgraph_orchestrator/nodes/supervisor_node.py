"""Supervisor node module for LangGraph orchestration.

This module determines the intent of the Relationship Manager's request
and routes the conversation to the appropriate specialist agent.
"""

from typing import Literal
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from pydantic import BaseModel, Field
import sys
import os

# Security: Enforce environment validation and inject injection scanner
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))
from shared.security_config import validate_environment, scan_for_injection, get_groq_api_key

validate_environment()

from langgraph_orchestrator.state import AgentState

class Route(BaseModel):
    """Schema defining the routing decision made by the supervisor.
    
    Attributes:
        next_node: The identifier of the next agent or '__end__' to terminate.
    """
    next_node: Literal["portfolio_agent", "__end__"] = Field(
        ...,
        description="The next node to route the conversation to. If the user asks about their portfolio, allocation, or wealth, route to 'portfolio_agent'. Otherwise route to '__end__'."
    )

# Simulates local execution via cloud endpoint for PoC performance.
# In production deployments, this relies on on-premise sovereign models.
llm = ChatGroq(
    model=os.getenv("GROQ_ROUTER_MODEL", "llama-3.3-70b-versatile"),
    api_key=get_groq_api_key(),
    temperature=0,
)
router_llm = llm.with_structured_output(Route)

system_prompt = """You are the Supervisor Node for Pramiti OS.
Your ONLY job is to determine the intent of the Relationship Manager's request.
If the RM is asking to view, analyze, or reallocate a client's portfolio, route to 'portfolio_agent'.
If it is generic chat, route to '__end__'.
"""

def supervisor_node(state: AgentState) -> dict:
    """Evaluates the conversation history and routes to the appropriate specialist agent.
    
    Checks for global kill-switch activation as part of the Model Risk Management 
    Framework (MRMF) before proceeding with model routing.
    
    Args:
        state: The current state of the LangGraph workflow, containing the message history.
        
    Returns:
        dict: A dictionary containing the `next_node` to transition to, or a termination 
              message if the kill-switch is active.
    """
    # MRMF Requirement: Hard Kill-Switch evaluation
    if os.getenv("KILL_SWITCH_ENABLED", "false").lower() == "true":
        from langchain_core.messages import AIMessage
        return {
            "messages": [AIMessage(content="⚠️ System override engaged: Copilot features are currently deactivated by Risk/IT. Please proceed with manual workflows.")],
            "next_node": "__end__"
        }

    messages = state.get("messages", [])
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("placeholder", "{messages}")
    ])
    
    chain = prompt | router_llm
    
    result: Route = chain.invoke({"messages": messages})  # type: ignore[assignment]
    return {"next_node": result.next_node}
