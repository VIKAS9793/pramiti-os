from mcp.server.fastmcp import FastMCP
import json
import os
from typing import Dict, Any

# Mock CBS database
MOCK_CBS_DB = {
    "CLIENT-001": {
        "client_id": "CLIENT-001",
        "kyc_status": "VERIFIED",
        "kyc_last_verified": "2025-10-15",
        "is_pep": False,
        "liquid_savings_balance_inr": 1500000,
        "primary_branch": "Mumbai Main"
    },
    "CLIENT-002": {
        "client_id": "CLIENT-002",
        "kyc_status": "EXPIRED",
        "kyc_last_verified": "2024-05-10",
        "is_pep": True,
        "liquid_savings_balance_inr": 85000000,
        "primary_branch": "Delhi South"
    }
}

mcp = FastMCP(
    name="CBS_Data_Server",
    instructions="Provides read-only access to the legacy Core Banking System (CBS) for KYC and balance checks."
)

@mcp.tool()
def get_client_kyc_and_balances(client_id: str) -> str:
    """
    Retrieve read-only KYC status, PEP (Politically Exposed Person) flags, and liquid savings balances from the Core Banking System.
    
    Args:
        client_id: The unique identifier for the client in the core banking system (e.g., 'CLIENT-001').
        
    Returns:
        JSON string containing the client's KYC and banking details, or an error if not found.
    """
    data = MOCK_CBS_DB.get(client_id)
    if not data:
        return json.dumps({"error": f"Client ID {client_id} not found in CBS."})
    
    return json.dumps(data)

if __name__ == "__main__":
    mcp.run()
