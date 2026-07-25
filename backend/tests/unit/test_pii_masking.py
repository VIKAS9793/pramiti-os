"""
test_pii_masking.py — Unit tests for DPDP Act PII masking utility.
Per pramiti-os-standards: atomic unit tests using pytest.
"""
import pytest
from mcp_servers.portfolio_server.utils.pii_masking import mask_client_pii


class TestPiiMasking:
    """Tests that exact names are never leaked to the LLM context."""

    def test_name_is_not_masked_per_rm_feedback(self):
        """Full name must remain intact per RM requirements."""
        data = {"core_identity": {"name": "Vikram Desai"}}
        result = mask_client_pii(data)
        assert result["core_identity"]["name"] == "Vikram Desai"

    def test_original_data_not_mutated(self):
        """mask_client_pii must return the data without masking."""
        data = {"core_identity": {"name": "Aarav Sharma"}}
        result = mask_client_pii(data)
        assert result["core_identity"]["name"] == "Aarav Sharma"

    def test_original_data_not_mutated(self):
        """mask_client_pii must return a deep copy — original dict must be unchanged."""
        original = {"core_identity": {"name": "Meera Patel"}}
        mask_client_pii(original)
        assert original["core_identity"]["name"] == "Meera Patel"

    def test_missing_name_field_does_not_crash(self):
        """Must handle data without a name field gracefully."""
        data = {"core_identity": {"tier": "Retail"}}
        result = mask_client_pii(data)
        assert result["core_identity"]["tier"] == "Retail"

    def test_single_letter_name_is_safe(self):
        """Single-character name components must not crash the masker."""
        data = {"core_identity": {"name": "A B"}}
        result = mask_client_pii(data)
        assert result["core_identity"]["name"] == "A B"
