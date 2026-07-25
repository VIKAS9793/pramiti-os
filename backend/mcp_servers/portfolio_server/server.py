"""Portfolio MCP Server module.

This module exposes client portfolio data securely via the Model Context Protocol, 
ensuring data is typed correctly and DPDP masking is applied before reaching the LLM.
"""

import json
import os
from pathlib import Path
from mcp.server.fastmcp import FastMCP
from pydantic import ValidationError
from mcp_servers.portfolio_server.models import ClientPortfolioResponse
from mcp_servers.portfolio_server.utils.pii_masking import mask_client_pii

mcp = FastMCP("Pramiti-Portfolio-Server")

DATA_DIR = Path(__file__).parent.parent / "data"
DATA_FILE = DATA_DIR / "mock_portfolios.json"

@mcp.tool()
def get_client_portfolio(client_id: str) -> str:
    """Fetches detailed portfolio allocation, health, and compliance status for a client.
    
    Loads mock JSON data, filters by client_id, applies PII masking according to 
    DPDP regulations, and validates the output schema before returning to the LLM.
    
    Args:
        client_id: The unique identifier for the client (e.g., CLI-1001).
        
    Returns:
        str: A JSON-serialized representation of the PII-masked client portfolio, 
             or an error JSON structure if not found or invalid.
    """
    try:
        if not DATA_FILE.exists():
            return json.dumps({"error": f"Database file not found at {DATA_FILE}"})
            
        with open(DATA_FILE, "r") as f:
            portfolios = json.load(f)
            
        client_data = next((p for p in portfolios if p["client_id"] == client_id), None)
        
        if not client_data:
            return json.dumps({"error": f"Client ID {client_id} not found."})
            
        # DPDP Act Compliance: Mask PII before returning
        masked_data = mask_client_pii(client_data)
        
        # Type Safety: Validate against Pydantic schema
        try:
            validated_response = ClientPortfolioResponse(**masked_data)
            return validated_response.model_dump_json()
        except ValidationError as ve:
            return json.dumps({"error": "Data validation failed", "details": str(ve)})
            
    except Exception as e:
        return json.dumps({"error": "Internal server error", "details": str(e)})

if __name__ == "__main__":
    mcp.run(transport='stdio')
