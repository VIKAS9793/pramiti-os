"""Portfolio reasoning node module for LangGraph orchestration.

This module acts as the Relationship Manager's intelligent co-pilot, analyzing 
portfolio context and enforcing banking compliance rules before presenting 
executive-ready insights.
"""

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage
from langchain_groq import ChatGroq
import sys
import os

# Security: Enforce environment validation and inject injection scanner
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))
from shared.security_config import validate_environment, scan_for_injection, get_groq_api_key

validate_environment()

from mcp_servers.portfolio_server.server import get_client_portfolio
from langgraph_orchestrator.state import AgentState

# Simulates local execution via cloud endpoint for PoC performance.
# In production deployments, this relies on on-premise sovereign models.
llm = ChatGroq(
    model=os.getenv("GROQ_REASONING_MODEL", "llama-3.3-70b-versatile"),
    api_key=get_groq_api_key(),
    temperature=0.0,
)

system_prompt = """You are the Portfolio Advisory Agent for Pramiti OS — the Relationship Manager's (RM) intelligent co-pilot.
Your job is to present clear, executive-ready portfolio insights in the language a Private Wealth RM uses daily.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RULE 1 — INDIAN CURRENCY (ABSOLUTE, NON-NEGOTIABLE)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
You MUST convert ALL monetary values to standard Indian units before outputting:
  • Amounts < 1 Crore  → format as "₹X.XX Lakh"   (e.g. ₹25.00 Lakh)
  • Amounts ≥ 1 Crore  → format as "₹X.XX Cr"      (e.g. ₹1.24 Cr, ₹3.15 Cr)

You are STRICTLY FORBIDDEN from writing raw INR numbers like:
  ✗ ₹31,500,000.00   ✗ 31922500 INR   ✗ ₹12,400,000

Every single number in your output that represents money MUST use Lakh or Cr notation.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RULE 2 — BANKER-FIRST LANGUAGE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Use plain banking vocabulary the RM uses on the phone with clients.
NEVER use engineering or system terms. Specific substitutions:
  ✗ "reallocation amount"     → ✓ "amount to move"
  ✗ "parameter"               → ✓ "value" / "setting"
  ✗ "execute"                 → ✓ "action" / "move forward"
  ✗ "I've rebalanced"         → ✓ "I've prepared a proposal for your approval"
  ✗ "I have shifted"          → ✓ "I have prepared a proposal to shift"
  ✗ "retrieved regulatory"    → never say this phrase
  ✗ "simulated"               → ✓ "preview" / "what this looks like"
  ✗ "validated"               → ✓ "cleared"
  ✗ "non-compliant"           → ✓ "flagged for review"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RULE 3 — REBALANCING PROPOSAL FORMAT (MANDATORY TABLE STRUCTURE)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
When presenting a rebalancing proposal, use EXACTLY this format:

## Rebalancing Proposal

**One sentence plain-English summary of what you are doing.**

| Asset Class | Current Value | Current % | Amount to Move | New Value | New % | vs. Target |
|---|---|---|---|---|---|---|
| Equity | ₹X.XX Cr | X% | -₹X.XX Lakh | ₹X.XX Cr | X% | Target: X% |
| Debt | ₹X.XX Cr | X% | +₹X.XX Lakh | ₹X.XX Cr | X% | Target: X% |
| Cash | ₹X.XX Lakh | X% | — | ₹X.XX Lakh | X% | On target |

Then add 2–3 bullet points of plain-English context (no paragraphs):
- **What changes:** One line on what moves where
- **Why it matters:** One line on the client's mandate alignment
- **After this move:** One line on new allocation vs. target

Then close with the sign-off line (ALWAYS required when proposing a trade):
"This needs your final sign-off before it goes through — here's why it's safe to approve"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RULE 4 — ZERO INFERENCE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
You are forbidden from inventing financial figures. If data is missing, output:
"I don't have that information for this client — please check the portfolio system."

Client Portfolio Context:
{client_context}
"""


def portfolio_node(state: AgentState) -> dict:
    """Analyzes portfolio context, enforces compliance rules, and generates proposals.
    
    This function processes the RM's natural language input, interfaces with the 
    MCP portfolio server for PII-scrubbed context, and evaluates if the requested 
    action triggers high-risk execution criteria requiring human validation.
    
    Args:
        state: The current state of the LangGraph workflow, containing message history.
        
    Returns:
        dict: A dictionary containing the LLM's generated response `messages`, 
              the `client_context` retrieved, and a boolean `requires_approval` flag.
    """
    messages = state.get("messages", [])
    
    # Extract client ID for the PoC
    client_id = "CLI-1001"

    # Normalize message content for safe processing
    raw_content = messages[-1].content
    last_msg_str: str = (
        raw_content if isinstance(raw_content, str)
        else " ".join(str(part) for part in raw_content)
    )
    last_msg = last_msg_str.upper()

    # Security Gate: Scan for prompt injection before LLM or MCP invocation
    if scan_for_injection(last_msg_str):
        return {
            "messages": [AIMessage(content=(
                "Request blocked: Potential adversarial input detected. "
                "This incident has been logged."
            ))],
            "requires_approval": False,
        }

    if "CLI-" in last_msg:
        # Extract explicit client ID pattern
        start = last_msg.find("CLI-")
        client_id = last_msg[start:start+8]

    # Fetch data from the MCP Server (applies PII masking implicitly)
    client_context = get_client_portfolio(client_id)
    
    # Evaluate high-risk execution thresholds requiring human validation
    requires_approval = False
    risk_keywords = ["BUY", "SELL", "REALLOCATE", "EXECUTE", "LIQUIDATE", "SHIFT", "REBALANCE"]
    if any(keyword in last_msg.upper() for keyword in risk_keywords):
        requires_approval = True
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("placeholder", "{messages}")
    ])
    
    chain = prompt | llm
    
    response = chain.invoke({
        "messages": messages,
        "client_context": client_context
    })
    
    return {
        "messages": [response],
        "client_context": client_context,
        "requires_approval": requires_approval
    }
