# Model Risk Management Framework (MRMF) Assessment
## Pramiti OS - AI Co-pilot & Compliance Engine

**Date:** July 25, 2026  
**Status:** Initial Assessment (Pilot Phase)  
**Classification:** Tiered Model (Material Impact on Customer Decisions)

---

## 1. Overview and Model Tiering
In alignment with the RBI Draft Guidance on Regulatory Principles for Model Risk Management (June 2026), the Pramiti OS AI Co-pilot and its accompanying rule-based Compliance Engine are formally classified as a **Tiered Model** within the bank's model inventory. Although the model operates in an "assistive" capacity (Human-in-the-Loop), its material influence on the Relationship Manager's (RM) decision-making process brings it within the expanded scope of the MRMF.

## 2. Mandatory Kill-Switch Capability
As required by the guidance, a platform-level kill switch has been implemented.
- **Mechanism:** The system checks a global environment variable (`KILL_SWITCH_ENABLED`) at the orchestrator layer (`supervisor_node.py`) before initiating any model calls.
- **Behavior:** If engaged by Risk or IT, the Copilot instantly halts all generative features across all active sessions. The UI degrades gracefully, instructing the RM to proceed with manual workflows. It prevents any degradation from being mistaken for a passed compliance check.

## 3. Seven AI Risk Dimensions Assessment

### 3.1 Explainability
- **Status:** Addressed & Mitigated.
- **Action Taken:** The system no longer relies on LLM-generated prose to explain compliance verdicts. The underlying reasoning (`explanation`) and specific regulatory citations (`citations`) are outputted as structured JSON payload and rendered deterministically in the UI.

### 3.2 Hallucination Risk
- **Status:** Mitigated.
- **Action Taken:** The temperature for both the reasoning model (`portfolio_node.py`) and the routing model (`supervisor_node.py`) has been set to `0.0` to eliminate creative variance. The compliance node operates strictly as a Retrieval-Augmented Generation (RAG) verifier, grounding all outputs against specific regulatory documents (e.g., SEBI/RBI).

### 3.3 Output Variability
- **Status:** Mitigated.
- **Action Taken:** By eliminating inference temperature and standardizing the UI rendering logic, the same query with the same portfolio state will yield the same structured verdict. Determinism is enforced at the LLM parameter level.

### 3.4 Data Risk (DPDP Compliance)
- **Status:** Addressed.
- **Action Taken:** Masking is rigorously applied at the backend processing layer (`pii_masking.py`). The LLM only processes masked names (e.g., "A**** S*****"). The frontend is responsible for re-hydrating the unmasked data for the authenticated RM, ensuring that third-party model providers never receive raw PII. 

### 3.5 Bias
- **Status:** Assessed, Low Risk.
- **Rationale:** The model acts primarily as an extraction and synthesis engine based on deterministic financial math and explicitly provided rules (e.g., Target Asset Allocation percentages). It does not score clients or recommend products based on demographic features.

### 3.6 Overfitting
- **Status:** Assessed, Low Risk.
- **Rationale:** The system leverages pre-trained foundational models (currently Llama-3.3 proxy, moving to sovereign models). The context is injected at runtime via zero-shot prompts and RAG, rather than fine-tuning the model on specific client portfolios, making overfitting inapplicable to the current architecture.

### 3.7 Spurious Correlations
- **Status:** Assessed, Low Risk.
- **Rationale:** The tool does not perform predictive analytics or unsupervised pattern matching. Recommendations are derived through strict mathematical calculation (variance from target allocation) and rule-based verification, effectively eliminating the risk of spurious correlations driving advisory actions.

## 4. Third-Party Accountability
The bank acknowledges that reliance on third-party foundation models (such as Groq or Sarvam) does not absolve it of accountability. This MRMF document, alongside the implementation of the platform-level kill switch and deterministic compliance rendering, forms the bank's independent validation and risk mitigation strategy. The bank owns the wrapper application, the data masking policies, and the final human-in-the-loop authorization gates.

---
*Approved by: [Pending Board Risk Committee Sign-off]*
