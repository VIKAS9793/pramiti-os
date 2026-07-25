"""
server.py — SIP Calculator MCP Server for Pramiti OS.

Per Architecture §2.1: Implements the `calculate_sip_return` MCP tool.
Formula: FV = P × [((1 + r)^n - 1) / r] × (1 + r)
  where P = monthly amount, r = monthly rate, n = duration in months.

Per PRD §6: Used by Portfolio Agent (Sarvam-105B / Groq proxy) to model
multi-product adoptions and SIP performance metrics for HNI clients.
"""
import json
import math
from mcp.server.fastmcp import FastMCP
from mcp_servers.sip_server.models import SIPReturnRequest, SIPReturnResponse
from pydantic import ValidationError

mcp = FastMCP("Pramiti-SIP-Calculator-Server")


@mcp.tool()
def calculate_sip_return(
    monthly_amount: float,
    duration_months: int,
    expected_return_pct: float,
) -> str:
    """
    Calculates projected SIP returns and estimated corpus for mutual fund planning.

    Args:
        monthly_amount: Monthly SIP contribution in INR (e.g., 50000).
        duration_months: Investment horizon in months (e.g., 120 for 10 years).
        expected_return_pct: Expected annual return rate in % (e.g., 12.0 for 12%).

    Returns:
        JSON string of SIPReturnResponse with corpus, gain, and CAGR.
    """
    # 1. Validate inputs via Pydantic schema
    try:
        req = SIPReturnRequest(
            monthly_amount=monthly_amount,
            duration_months=duration_months,
            expected_return_pct=expected_return_pct,
        )
    except ValidationError as ve:
        return json.dumps({"error": "Invalid input parameters", "details": str(ve)})

    # 2. Core SIP formula (standard Indian mutual fund calculation)
    # Monthly interest rate
    r = req.expected_return_pct / 100 / 12

    # Future Value of SIP: FV = P × [((1 + r)^n - 1) / r] × (1 + r)
    n = req.duration_months
    p = req.monthly_amount

    if r == 0:
        # Edge case: 0% return → straight sum
        corpus = p * n
    else:
        corpus = p * (((1 + r) ** n - 1) / r) * (1 + r)

    total_invested = p * n
    gain = corpus - total_invested
    absolute_return_pct = (gain / total_invested) * 100 if total_invested > 0 else 0

    # CAGR from SIP corpus: annualised effective return
    # Approximated from total invested → corpus over full horizon
    years = n / 12
    if years > 0 and total_invested > 0:
        cagr = (math.pow(corpus / total_invested, 1 / years) - 1) * 100
    else:
        cagr = 0.0

    # 3. Build and validate the response schema
    response = SIPReturnResponse(
        monthly_amount_inr=round(p, 2),
        duration_months=n,
        expected_annual_return_pct=req.expected_return_pct,
        total_invested_inr=round(total_invested, 2),
        estimated_corpus_inr=round(corpus, 2),
        estimated_gain_inr=round(gain, 2),
        absolute_return_pct=round(absolute_return_pct, 2),
        cagr_pct=round(cagr, 2),
    )

    return response.model_dump_json()


if __name__ == "__main__":
    mcp.run(transport="stdio")
