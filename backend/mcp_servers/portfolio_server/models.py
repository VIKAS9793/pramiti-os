"""Data models for the Portfolio MCP Server.

This module defines Pydantic models used for input validation and output schema 
enforcement when interacting with the portfolio data.
"""

from pydantic import BaseModel, Field
from typing import List, Optional

class ClientPortfolioRequest(BaseModel):
    client_id: str = Field(..., description="The unique identifier for the client (e.g., CLI-1001)")

class CoreIdentity(BaseModel):
    name: str = Field(..., description="Masked name of the client")
    tier: str = Field(..., description="Wealth management tier")
    kyc_status: str = Field(..., description="Current KYC compliance status")
    risk_appetite: str = Field(..., description="Risk profile of the client")
    age: int = Field(..., description="Age of the client")

class PortfolioHealth(BaseModel):
    total_aum_inr: float
    unrealized_pnl_inr: float
    unrealized_pnl_pct: float

class Allocation(BaseModel):
    equity_pct: float
    debt_pct: float
    alternatives_pct: float
    cash_pct: float

class Holding(BaseModel):
    asset_name: str
    category: str
    current_value_inr: float
    allocation_pct: float
    sip_active: bool
    sip_amount: float

class SipDetails(BaseModel):
    total_monthly_sip_inr: float
    next_sip_date: Optional[str]
    sip_status: str

class ActionableIntelligence(BaseModel):
    next_important_date: str
    recent_interaction: str
    flags: List[str]

class ClientPortfolioResponse(BaseModel):
    client_id: str
    description: str
    core_identity: CoreIdentity
    portfolio_health: PortfolioHealth
    allocation: Allocation
    holdings: List[Holding]
    sip_details: SipDetails
    actionable_intelligence: ActionableIntelligence
