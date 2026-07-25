"""
models.py — Pydantic schemas for the SIP Calculator MCP Server.
Per pramiti-os-standards: all MCP tool I/O validated via Pydantic v2.
"""
from pydantic import BaseModel, Field, field_validator


class SIPReturnRequest(BaseModel):
    """Input schema for the calculate_sip_return MCP tool."""
    monthly_amount: float = Field(..., gt=0, description="Monthly SIP contribution in INR.")
    duration_months: int = Field(..., gt=0, le=600, description="Investment horizon in months (max 50 years).")
    expected_return_pct: float = Field(..., gt=0, lt=100, description="Expected annual return rate in % (e.g., 12.0 for 12%).")

    @field_validator("expected_return_pct")
    @classmethod
    def validate_return_rate(cls, v: float) -> float:
        if v > 50:
            raise ValueError("Expected return % above 50% is not a realistic financial input.")
        return v


class SIPReturnResponse(BaseModel):
    """Output schema for the calculate_sip_return MCP tool."""
    monthly_amount_inr: float = Field(..., description="Monthly SIP contribution in INR.")
    duration_months: int = Field(..., description="Investment horizon in months.")
    expected_annual_return_pct: float = Field(..., description="Expected annual return rate in %.")
    total_invested_inr: float = Field(..., description="Total capital invested (monthly_amount × duration_months).")
    estimated_corpus_inr: float = Field(..., description="Estimated future value of the SIP corpus.")
    estimated_gain_inr: float = Field(..., description="Total estimated gain (corpus - invested).")
    absolute_return_pct: float = Field(..., description="Absolute return as a percentage of invested capital.")
    cagr_pct: float = Field(..., description="Compounded Annual Growth Rate (CAGR) of the SIP.")
