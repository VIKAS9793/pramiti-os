"""
test_sip_server.py — Unit tests for the SIP Calculator MCP tool.

Covers the full spectrum of Indian retail domestic investor scenarios:
  - New to market / financial literacy level: Low, Moderate, High
  - Rookie (short horizon, small SIP) → Expert/Veteran (large corpus, optimised inputs)
  - Edge cases: zero return, maximum duration, unrealistic return rate inputs
  - Sad paths: negative amount, invalid types, extreme values

Per pramiti-os-standards: atomic pytest test classes, no external dependencies.
"""
import json
import pytest
from mcp_servers.sip_server.server import calculate_sip_return


class TestSIPReturnHappyPaths:
    """Standard scenarios across investor literacy levels."""

    def test_new_investor_first_sip(self):
        """
        LOW LITERACY — New-to-market investor starting first SIP.
        ₹5,000/month for 3 years (36 months) at 8% (conservative estimate).
        Corpus should be meaningfully more than ₹1,80,000 invested.
        """
        result = json.loads(calculate_sip_return(5000, 36, 8.0))
        assert "error" not in result
        assert result["total_invested_inr"] == 180000.0
        assert result["estimated_corpus_inr"] > 180000.0
        assert result["estimated_gain_inr"] > 0

    def test_moderate_investor_10year_horizon(self):
        """
        MODERATE LITERACY — Salaried professional, 10-year SIP.
        ₹25,000/month for 120 months at 12% (typical equity mutual fund expectation).
        """
        result = json.loads(calculate_sip_return(25000, 120, 12.0))
        assert "error" not in result
        assert result["total_invested_inr"] == 3_000_000.0  # ₹30 Lakh
        assert result["estimated_corpus_inr"] > 5_000_000.0  # Should cross ₹50L
        assert result["cagr_pct"] > 0

    def test_hni_veteran_long_horizon(self):
        """
        HIGH LITERACY / EXPERT — HNI investor, 25-year SIP.
        ₹1,00,000/month for 300 months at 13% (actively managed large-cap).
        Corpus should exceed ₹5 Cr.
        """
        result = json.loads(calculate_sip_return(100000, 300, 13.0))
        assert "error" not in result
        assert result["estimated_corpus_inr"] > 50_000_000.0  # ₹5 Cr+
        assert result["absolute_return_pct"] > 100  # More than doubled

    def test_rookie_monthly_micro_sip(self):
        """
        ROOKIE — Gig worker, micro-SIP of ₹500/month for 1 year.
        Small amounts must compute correctly without floating point errors.
        """
        result = json.loads(calculate_sip_return(500, 12, 10.0))
        assert "error" not in result
        assert result["total_invested_inr"] == 6000.0
        assert result["estimated_corpus_inr"] > 6000.0
        assert result["estimated_corpus_inr"] < 7000.0  # Sanity bound

    def test_ppf_conservative_return_rate(self):
        """
        CONSERVATIVE — PPF-equivalent return at 7.1%.
        Validates that low return rates (government scheme parity) compute correctly.
        """
        result = json.loads(calculate_sip_return(10000, 60, 7.1))
        assert "error" not in result
        assert result["estimated_corpus_inr"] > 600000.0  # ₹6L invested → more than that

    def test_elss_tax_saver_3year_lock_in(self):
        """
        TAX-SAVER INVESTOR — ELSS fund with 3-year lock-in (standard deduction play).
        ₹12,500/month (₹1.5L annual — Section 80C limit), 36 months at 14%.
        """
        result = json.loads(calculate_sip_return(12500, 36, 14.0))
        assert "error" not in result
        assert result["total_invested_inr"] == 450000.0
        assert result["estimated_corpus_inr"] > 500000.0


class TestSIPReturnEdgeCases:
    """Boundary and ambiguous inputs."""

    def test_single_month_sip(self):
        """
        EDGE CASE: 1-month SIP (lump sum equivalent).
        Should compute without division errors.
        """
        result = json.loads(calculate_sip_return(100000, 1, 12.0))
        assert "error" not in result
        assert result["total_invested_inr"] == 100000.0
        # 1 month — gain should be negligible but positive
        assert result["estimated_corpus_inr"] >= 100000.0

    def test_maximum_50_year_horizon(self):
        """
        EDGE CASE: 600 months (50 years) — maximum allowed.
        Should not overflow or produce NaN.
        """
        result = json.loads(calculate_sip_return(1000, 600, 12.0))
        assert "error" not in result
        assert result["estimated_corpus_inr"] > 0
        assert result["cagr_pct"] > 0

    def test_very_low_return_1_percent(self):
        """
        EDGE CASE: 1% annual return (liquid fund equivalent).
        """
        result = json.loads(calculate_sip_return(10000, 12, 1.0))
        assert "error" not in result
        # Almost no gain expected
        assert result["estimated_gain_inr"] > 0
        assert result["estimated_gain_inr"] < 1000  # Sanity — less than ₹1000 gain on ₹1.2L

    def test_large_inr_amount_no_overflow(self):
        """
        EDGE CASE: Ultra-HNI, ₹10,00,000/month SIP.
        Must not overflow or produce scientific notation errors.
        """
        result = json.loads(calculate_sip_return(1_000_000, 120, 12.0))
        assert "error" not in result
        assert result["estimated_corpus_inr"] > 100_000_000.0  # ₹10 Cr+

    def test_return_fields_are_consistent(self):
        """
        INVARIANT: corpus = invested + gain (within float tolerance).
        """
        result = json.loads(calculate_sip_return(20000, 60, 10.0))
        reconstructed = result["total_invested_inr"] + result["estimated_gain_inr"]
        assert abs(result["estimated_corpus_inr"] - reconstructed) < 1.0  # ₹1 tolerance


class TestSIPReturnSadPaths:
    """Invalid and adversarial inputs — all must return structured errors, never crash."""

    def test_negative_monthly_amount_rejected(self):
        """SAD PATH: Negative SIP amount is not valid."""
        result = json.loads(calculate_sip_return(-5000, 60, 12.0))
        assert "error" in result

    def test_zero_monthly_amount_rejected(self):
        """SAD PATH: Zero SIP amount is not valid."""
        result = json.loads(calculate_sip_return(0, 60, 12.0))
        assert "error" in result

    def test_zero_duration_rejected(self):
        """SAD PATH: Zero duration is not a valid SIP."""
        result = json.loads(calculate_sip_server := calculate_sip_return(5000, 0, 12.0))
        assert "error" in result

    def test_above_50pct_return_rejected(self):
        """
        SAD PATH — HALLUCINATION GUARD:
        A new-to-market investor might be misled by bad advice promising 60%+ returns.
        The validator must block this as an unrealistic financial input.
        """
        result = json.loads(calculate_sip_return(5000, 12, 60.0))
        assert "error" in result

    def test_100pct_return_rejected(self):
        """SAD PATH: 100% return rate is nonsensical and must be blocked."""
        result = json.loads(calculate_sip_return(5000, 12, 100.0))
        assert "error" in result

    def test_duration_above_600_rejected(self):
        """SAD PATH: Duration above 600 months (50 years) is beyond a realistic lifecycle."""
        result = json.loads(calculate_sip_return(5000, 601, 12.0))
        assert "error" in result

    def test_negative_return_rate_rejected(self):
        """SAD PATH: Negative return rate is not valid for SIP computation."""
        result = json.loads(calculate_sip_return(5000, 60, -5.0))
        assert "error" in result
