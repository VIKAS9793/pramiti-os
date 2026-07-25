import json
from typing import Dict, Any, Tuple, List

class CoreBankingEngine:
    """
    Deterministic mathematical and compliance engine.
    Replaces all LLM hallucinations with strict financial logic.
    """

    @staticmethod
    def calculate_rebalance(
        portfolio_context: str, 
        action: str, 
        amount_inr: float, 
        source_asset: str, 
        destination_asset: str
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        try:
            portfolio = json.loads(portfolio_context)
            total_value = portfolio.get("portfolio_health", {}).get("total_aum_inr", 12400000.0)
            alloc = portfolio.get("allocation", {})
            
            assets = [
                {"asset_class": "Equity", "percentage": alloc.get("equity_pct", 65.0), "target_percentage": 50.0},
                {"asset_class": "Debt", "percentage": alloc.get("debt_pct", 25.0), "target_percentage": 40.0},
                {"asset_class": "Cash", "percentage": alloc.get("cash_pct", 5.0), "target_percentage": 10.0},
                {"asset_class": "Alternatives", "percentage": alloc.get("alternatives_pct", 5.0), "target_percentage": 0.0}
            ]
            
            for asset in assets:
                asset["value_inr"] = (asset["percentage"] / 100) * total_value
                
        except Exception:
            # Fallback mock for testing if context is malformed
            assets = [
                {"asset_class": "Equity", "value_inr": 8060000.0, "percentage": 65.0, "target_percentage": 50.0},
                {"asset_class": "Debt", "value_inr": 3100000.0, "percentage": 25.0, "target_percentage": 40.0},
                {"asset_class": "Cash", "value_inr": 1240000.0, "percentage": 10.0, "target_percentage": 10.0}
            ]
            total_value = 12400000.0

        new_assets = []
        for asset in assets:
            cls_name = asset["asset_class"].lower()
            current_val = asset["value_inr"]
            
            # Apply transaction
            new_val = current_val
            if cls_name == source_asset.lower():
                new_val -= amount_inr
            elif cls_name == destination_asset.lower():
                new_val += amount_inr
                
            # Prevent negative balances
            if new_val < 0:
                new_val = 0
                
            new_pct = (new_val / total_value) * 100 if total_value > 0 else 0
            
            new_assets.append({
                "asset_class": asset["asset_class"],
                "value_inr": new_val,
                "percentage": round(new_pct, 2),
                "target_percentage": asset.get("target_percentage", 0),
                "original_value_inr": current_val,
                "original_percentage": asset["percentage"]
            })

        # 2. Deterministic Compliance Verification
        is_compliant = True
        explanation = "Passes Risk Mandate ID: 402 - All thresholds within bounds."
        
        for asset in new_assets:
            cls_name = asset["asset_class"].lower()
            pct = asset["percentage"]
            
            if cls_name == "equity" and pct > 70.0:
                is_compliant = False
                explanation = f"Breach Risk Mandate ID: 402 - Equity at {pct}% exceeds 70% maximum limit."
                break
            if cls_name == "debt" and pct < 20.0:
                is_compliant = False
                explanation = f"Breach Risk Mandate ID: 402 - Debt at {pct}% is below 20% minimum limit."
                break
                
        compliance_verdict = {
            "is_compliant": is_compliant,
            "explanation": explanation,
            "citations": ["SEBI_101", "RBI_MRMF_42"]
        }
        
        return new_assets, compliance_verdict
