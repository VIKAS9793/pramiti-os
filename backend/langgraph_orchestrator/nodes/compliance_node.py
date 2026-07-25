"""Compliance verification node module for LangGraph orchestration.

This module enforces strict deterministic regulatory constraints 
derived from the Core Banking Engine, replacing previous generative 
LLM compliance checks which were prone to hallucinations.
"""

from langchain_core.messages import AIMessage
import re
import json
from langgraph_orchestrator.state import AgentState

def compliance_node(state: AgentState) -> dict:
    """Evaluates the generated portfolio proposal against deterministic rules.
    
    Extracts the deterministic compliance verdict embedded by the portfolio 
    node and surfaces it securely to the UI, bypassing LLM generative logic.
    
    Args:
        state: The current state of the LangGraph workflow.
        
    Returns:
        dict: A dictionary containing the updated `messages` list with the 
              strict compliance verdict appended.
    """
    messages = state.get("messages", [])
    
    raw_content = messages[-1].content
    proposal_str = (
        raw_content if isinstance(raw_content, str)
        else " ".join(str(part) for part in raw_content)
    )

    # Extract the deterministic compliance payload
    pattern = r"<!-- DETERMINISTIC_COMPLIANCE:\s*(.*?)\s*-->"
    match = re.search(pattern, proposal_str, re.DOTALL)
    
    if match:
        compliance_json_str = match.group(1)
        try:
            compliance_data = json.loads(compliance_json_str)
            # Remove the hidden block from the visible proposal string
            clean_proposal = re.sub(pattern, "", proposal_str).strip()
            
            payload = {
                "is_compliant": compliance_data.get("is_compliant", False),
                "explanation": compliance_data.get("explanation", "System error reading compliance data."),
                "citations": compliance_data.get("citations", [])
            }
            
            report_text = f"\n\n<compliance_verdict>\n{json.dumps(payload)}\n</compliance_verdict>\n\n"
            new_proposal_text = clean_proposal + "\n" + report_text
            
            new_messages = messages.copy()
            new_messages[-1] = AIMessage(content=new_proposal_text)

            return {
                "messages": new_messages,
                "requires_approval": state.get("requires_approval", True)
            }
            
        except json.JSONDecodeError:
            pass

    # Fallback if deterministic compliance is missing
    fallback_payload = {
        "is_compliant": False,
        "explanation": "Fatal Error: Deterministic compliance payload missing. Halting execution to prevent MRMF violation.",
        "citations": ["RBI_MRMF_42_KILL_SWITCH"]
    }
    fallback_text = f"\n\n<compliance_verdict>\n{json.dumps(fallback_payload)}\n</compliance_verdict>\n\n"
    new_messages = messages.copy()
    new_messages[-1] = AIMessage(content=proposal_str + fallback_text)
    
    return {
        "messages": new_messages,
        "requires_approval": state.get("requires_approval", True)
    }
