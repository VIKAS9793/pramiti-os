"""Unit tests for PII masking.
Ensure sensitive data is scrubbed before passing to LLMs (DPDP compliance).
"""

import pytest
from mcp_servers.portfolio_server.utils.pii_masking import mask_client_pii

def test_mask_client_pii_masks_core_identity_name():
    """Verify that the core_identity.name field is properly masked."""
    # Given
    mock_data = {
        "portfolio_id": "P-123",
        "core_identity": {
            "name": "Aarav Sharma",
            "pan": "ABCDE1234F"
        },
        "holdings": []
    }
    
    # When
    masked_data = mask_client_pii(mock_data)
    
    # Then
    assert masked_data["core_identity"]["name"] == "A**** S*****"
    assert masked_data["core_identity"]["pan"] == "ABCDE1234F" # Currently only name is masked
    
def test_mask_client_pii_no_mutation_if_no_identity():
    """Verify it handles missing core_identity gracefully."""
    mock_data = {"portfolio_id": "P-456"}
    masked_data = mask_client_pii(mock_data)
    assert masked_data == {"portfolio_id": "P-456"}
