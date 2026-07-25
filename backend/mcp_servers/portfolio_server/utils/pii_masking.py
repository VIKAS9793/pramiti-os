"""PII Masking utilities.

This module provides functions to sanitize sensitive client data in accordance 
with the Digital Personal Data Protection (DPDP) Act before it is consumed 
by external systems or LLMs.
"""

import copy

def mask_client_pii(portfolio_data: dict) -> dict:
    """Masks personally identifiable information in the portfolio data.
    
    Applies data minimization rules to ensure sensitive names are partially 
    redacted (e.g., "Aarav Sharma" to "A**** S*****") while retaining the 
    underlying object structure.
    
    Args:
        portfolio_data: The raw dictionary containing client portfolio information.
        
    Returns:
        dict: A deep copy of the portfolio data with the `client_name` field masked.
    """
    masked_data = copy.deepcopy(portfolio_data)
    if "client_name" in masked_data:
        name_parts = masked_data["client_name"].split(" ")
        masked_parts = [f"{part[0]}{'*' * (len(part) - 1)}" for part in name_parts if len(part) > 0]
        masked_data["client_name"] = " ".join(masked_parts)
    
    return masked_data
