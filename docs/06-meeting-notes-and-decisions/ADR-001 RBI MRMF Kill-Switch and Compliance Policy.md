# Architecture Decision Record (ADR-001): RBI MRMF Kill-Switch & Human-in-the-Loop Implementation

**Status**: **APPROVED**  
**Date**: 2026-07-24  
**Deciders**: Chief Risk Officer, Lead Architect, Principal AI Product Manager  
**Regulatory Drivers**: RBI Draft Guidance on Model Risk Management Framework (Press Release No. 2026-2027/528, June 24, 2026) & SEBI Advisory Circular HO/13/19/12(1)2026-ITD-1_CIMGI/10873/2026.  

---

## 1. Context & Regulatory Imperative

The RBI Model Risk Management Framework (MRMF) mandates that financial institutions operating AI/ML systems must enforce two critical technical controls:
1. **Mandatory Kill Switch**: The infrastructure must possess an instantaneous override/deactivation mechanism to halt anomalous or uncalibrated AI outputs before state-changing execution.
2. **Human-in-the-Loop Oversight**: Algorithmic financial recommendations (credit, wealth, advisory) cannot execute autonomously without explicit, logged human validation to mitigate "automation bias" and "decision fatigue."

---

## 2. Decision Considered

We evaluated three potential implementation patterns for enforcing human validation and execution halting:

* **Option A: Post-hoc Human Audit (Asynchronous Review)**  
  * *Description*: AI executes recommendations immediately; human reviews logs post-facto.  
  * *Verdict*: **REJECTED**. Violates RBI MRMF mandates against autonomous execution.

* **Option B: Application-Layer Checkboxes in UI**  
  * *Description*: AI returns output to frontend UI; frontend relies on a user submission button to call the final API.  
  * *Verdict*: **REJECTED**. Vulnerable to UI bypass, client-side tampering, and API bypass under SEBI CSCRF audit rules.

* **Option C: Graph-Level Interrupt Nodes via LangGraph (`interrupt_before`)**  
  * *Description*: Embed state-halting logic directly into the LangGraph state machine execution loop using `interrupt_before=["human_review"]`.  
  * *Verdict*: **APPROVED**. Programmatically guarantees that graph execution physically stops at the graph runtime layer.

---

## 3. Approved Architecture Specification

```python
# Programmatic Graph Halting (RBI Kill-Switch Compliance)
workflow.add_node("human_review", human_review_node)

# LangGraph runtime halts execution BEFORE executing 'human_review'
app = workflow.compile(
    checkpointer=checkpointer,
    interrupt_before=["human_review"] # Halts execution engine
)
```

### Key Technical Guarantees:
1. **State Persistence**: The current graph state (`AgentState`) is serialized to PostgreSQL via `PostgresSaver`.
2. **Deterministic Resume**: Graph can ONLY resume when the Relationship Manager explicitly sends an `APPROVED` signal with a signed JWT token.
3. **Immutable Audit Trail**: The RM decision, timestamp, and prompt/completion tokens are written to `rbi_mrmf_audit_logs` for mandatory 10-year retention.
