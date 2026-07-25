"""Portfolio reasoning node module for LangGraph orchestration.

This module acts as the Relationship Manager's intelligent co-pilot.
It strictly uses the LLM to extract intent from natural language, 
and relies on the Core Banking Engine for deterministic financial math.
"""

from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage
from langchain_groq import ChatGroq
import sys
import os
import json

# Security: Enforce environment validation and inject injection scanner
from shared.security_config import validate_environment, scan_for_injection, get_groq_api_key

validate_environment()

from mcp_servers.portfolio_server.server import get_client_portfolio
from mcp_servers.cbs_server import get_client_kyc_and_balances
from langgraph_orchestrator.state import AgentState
from langgraph_orchestrator.services.core_banking_engine import CoreBankingEngine

llm = ChatGroq(
    model=os.getenv("GROQ_REASONING_MODEL", "llama-3.3-70b-versatile"),
    api_key=get_groq_api_key(),
    temperature=0.0,
)

class RebalanceIntent(BaseModel):
    """Schema for extracting the RM's trading intent."""
    action: str = Field(description="The action being performed, e.g., 'reallocate', 'buy', 'sell'")
    amount_inr: float = Field(description="The precise absolute amount to move in INR. Convert Lakhs/Crores to exact digits (e.g. 10 Lakhs = 1000000.0).")
    source_asset: str = Field(description="The asset class to sell or move money from (e.g., 'Equity', 'Debt'). Use 'None' if NA.")
    destination_asset: str = Field(description="The asset class to buy or move money to (e.g., 'Debt', 'Equity'). Use 'None' if NA.")

system_prompt = """You are an Intent Extractor for the Pramiti OS Advisory Copilot.
Your ONLY job is to parse the user's natural language input and extract their trading intent.
If they say "reallocate 10 Lakhs from equity to debt", you extract amount=1000000.0, source='Equity', destination='Debt'.
DO NOT do any math or generate conversational text. Just extract the structured data.
"""

def format_currency(value: float) -> str:
    """Format INR strictly into Lakhs or Crores."""
    if value >= 10000000:
        return f"₹{value / 10000000:.2f} Cr"
    else:
        return f"₹{value / 100000:.2f} Lakh"

def portfolio_node(state: AgentState) -> dict:
    """Extracts intent and deterministically computes portfolio shifts.
    
    Args:
        state: The current state of the LangGraph workflow.
        
    Returns:
        dict: Updated state with the exact deterministic markdown table response.
    """
    messages = state.get("messages", [])
    
    client_id = "CLI-1001"
    cbs_client_id = "CLIENT-001"

    raw_content = messages[-1].content
    last_msg_str: str = (
        raw_content if isinstance(raw_content, str)
        else " ".join(str(part) for part in raw_content)
    )
    last_msg = last_msg_str.upper()

    if scan_for_injection(last_msg_str):
        return {
            "messages": [AIMessage(content="Request blocked: Potential adversarial input detected. This incident has been logged.")],
            "requires_approval": False,
        }

    if "CLI-" in last_msg:
        start = last_msg.find("CLI-")
        client_id = last_msg[start:start+8]
        if client_id == "CLI-1002":
            cbs_client_id = "CLIENT-002"

    client_context = get_client_portfolio(client_id)
    cbs_context = get_client_kyc_and_balances(cbs_client_id)
    
    requires_approval = False
    risk_keywords = ["BUY", "SELL", "REALLOCATE", "EXECUTE", "LIQUIDATE", "SHIFT", "REBALANCE"]
    if any(keyword in last_msg.upper() for keyword in risk_keywords):
        requires_approval = True
        
    # Extractor LLM
    structured_llm = llm.with_structured_output(RebalanceIntent)
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("placeholder", "{messages}")
    ])
    chain = prompt | structured_llm
    
    intent: RebalanceIntent = chain.invoke({"messages": messages})
    
    # Deterministic Engine
    new_assets, compliance_verdict = CoreBankingEngine.calculate_rebalance(
        portfolio_context=client_context,
        action=intent.action,
        amount_inr=intent.amount_inr,
        source_asset=intent.source_asset,
        destination_asset=intent.destination_asset
    )
    
    # Programmatically construct output
    action_desc = f"I have prepared a proposal to shift {format_currency(intent.amount_inr)} from {intent.source_asset.capitalize()} to {intent.destination_asset.capitalize()}."
    
    table_lines = [
        "## Rebalancing Proposal",
        "",
        f"**{action_desc}**",
        "",
        "| Asset Class | Current Value | Current % | Amount to Move | New Value | New % | vs. Target |",
        "|---|---|---|---|---|---|---|"
    ]
    
    for asset in new_assets:
        cls_name = asset["asset_class"].capitalize()
        curr_val = format_currency(asset["original_value_inr"])
        curr_pct = f"{asset['original_percentage']}%"
        target_pct = asset["target_percentage"]
        new_val = format_currency(asset["value_inr"])
        new_pct = f"{asset['percentage']}%"
        
        move = "—"
        if cls_name.lower() == intent.source_asset.lower():
            move = f"-{format_currency(intent.amount_inr)}"
        elif cls_name.lower() == intent.destination_asset.lower():
            move = f"+{format_currency(intent.amount_inr)}"
            
        vs_target = "On target" if asset['percentage'] == target_pct else f"Target: {target_pct}%"
        
        table_lines.append(f"| {cls_name} | {curr_val} | {curr_pct} | {move} | {new_val} | {new_pct} | {vs_target} |")
        
    table_lines.extend([
        "",
        "- **What changes:** Shifting funds to realign with the model portfolio mandate.",
        "- **Why it matters:** Eliminates drift and strictly aligns with the client's risk profile.",
        "",
        "This needs your final sign-off before it goes through."
    ])
    
    response_text = "\n".join(table_lines)
    
    # Append raw JSON payload for compliance_node to parse
    response_text += f"\n\n<!-- DETERMINISTIC_COMPLIANCE: {json.dumps(compliance_verdict)} -->"
    
    return {
        "messages": [AIMessage(content=response_text)],
        "client_context": client_context,
        "requires_approval": requires_approval
    }
