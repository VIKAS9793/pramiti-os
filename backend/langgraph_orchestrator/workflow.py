"""Workflow definition for LangGraph orchestration.

This module wires together the LangGraph state graph, configuring nodes, 
edges, and conditional routing logic for the Pramiti OS multi-agent system, 
including MRMF compliance interrupts and ambiguity checkpoints.
"""

from langgraph.graph import StateGraph, END, START
from langgraph.checkpoint.memory import InMemorySaver
from langgraph_orchestrator.state import AgentState
from langgraph_orchestrator.nodes.supervisor_node import supervisor_node
from langgraph_orchestrator.nodes.portfolio_node import portfolio_node
from langgraph_orchestrator.nodes.compliance_node import compliance_node
from langgraph_orchestrator.nodes.ambiguity_node import ambiguity_node

def compile_workflow():
    """Compiles the Pramiti OS LangGraph workflow.
    
    Wires the nodes together and enforces the RBI MRMF NodeInterrupt 
    and Ambiguity Clarification.
    
    Returns:
        CompiledGraph: The compiled state graph ready for execution.
    """
    workflow = StateGraph(AgentState)  # type: ignore[type-var]
    
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("ambiguity_checker", ambiguity_node)
    workflow.add_node("portfolio_agent", portfolio_node)
    workflow.add_node("compliance_checker", compliance_node)
    
    workflow.add_conditional_edges(
        "supervisor",
        lambda x: x["next_node"],
        {
            "portfolio_agent": "ambiguity_checker", 
            "__end__": END
        }
    )

    def check_ambiguity(state: AgentState) -> str:
        if state.get("requires_clarification", False):
            return "__end__"
        return "portfolio_agent"

    workflow.add_conditional_edges(
        "ambiguity_checker",
        check_ambiguity,
        {
            "portfolio_agent": "portfolio_agent",
            "__end__": END
        }
    )
    
    def check_approval(state: AgentState) -> str:
        if state.get("requires_approval", False):
            return "compliance_checker"
        return "__end__"

    workflow.add_conditional_edges(
        "portfolio_agent",
        check_approval,
        {
            "compliance_checker": "compliance_checker",
            "__end__": END
        }
    )
        
    def human_review_node(state: AgentState) -> dict:
        """Interrupt target node for RBI MRMF Kill-Switch.
        
        Execution is paused BEFORE this node runs via interrupt_before=[].
        If reached, it is a passthrough — the RM has approved and the workflow ends.
        
        Args:
            state: The current state of the LangGraph workflow.
            
        Returns:
            dict: An empty dictionary, acting as a passthrough.
        """
        return {}

    workflow.add_node("human_review", human_review_node)
    
    workflow.add_edge("compliance_checker", "human_review")
    workflow.add_edge("human_review", END)
    
    workflow.add_edge(START, "supervisor")
    
    memory = InMemorySaver()
    
    app = workflow.compile(
        checkpointer=memory,
        interrupt_before=["human_review"]
    )
    
    return app

app = compile_workflow()
