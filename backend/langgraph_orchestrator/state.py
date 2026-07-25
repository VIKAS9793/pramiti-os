"""State definitions for LangGraph orchestration.

This module defines the typed state dictionary used to pass context, 
messages, and workflow flags between nodes in the Pramiti OS multi-agent graph.
"""

from typing import Annotated, Sequence
from typing_extensions import TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """Strict TypedDict representing the state of the Pramiti OS multi-agent graph.
    
    Attributes:
        messages: Accumulated message history using LangGraph's add_messages reducer.
        client_context: Portfolio JSON or other context injected from MCP Tools.
        next_node: Routing indicator for the supervisor node.
        requires_approval: Flag to trigger RBI MRMF NodeInterrupt for high-risk actions.
        requires_clarification: Flag indicating ambiguous transactional intent requiring RM input.
    """
    messages: Annotated[list[BaseMessage], add_messages]
    client_context: str
    next_node: str
    requires_approval: bool
    requires_clarification: bool
