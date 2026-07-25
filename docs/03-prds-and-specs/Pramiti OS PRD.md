# Product Requirements Document (PRD): Pramiti OS

**Product Name**: Pramiti OS  
**Document Owner**: Vikas Dayashankar Sahani  
**Target Role Segment**: Product Strategy / Technical Product Management  
**Status**: MVP Draft (OEM & Regulatory Verified)  

---

## 1. Executive Summary & Core Thesis

Front-line retail banking and wealth management operations are bottlenecked by system fragmentation. Relationship Managers (RMs) face immense cognitive load toggling between core banking ledgers, legacy CRMs, and live market terminals.

**Pramiti OS** is a multi-agent artificial intelligence platform designed to assist Relationship Managers. Unlike standard B2C LLM wrappers that risk violating the DPDP Act 2023 and the RBI Model Risk Management Framework (MRMF Draft Guidance, June 2026), Pramiti OS utilizes a decoupled architecture. It leverages a stateful graph (LangGraph) to query internal enterprise data through MCP tools, generating financial insights while requiring explicit "human-in-the-loop" oversight and supporting data localization.

---

## 2. Target Personas & Jobs-To-Be-Done (JTBD)

> 📘 **Full JTBD Specification**: See [`User Personas and JTBD.md`](https://github.com/VIKAS9793/pramiti-os/blob/main/docs/02-research-and-discovery/User%20Personas%20and%20JTBD.md) for the complete Outcome-Driven Innovation (ODI) matrix and 8-step job map.

* **Primary Persona**: Front-line Relationship Managers (NISM Series V-A / IRDAI certified) managing ₹150+ Cr AUM.
* **Secondary Personas**: High-Net-Worth Individual (HNI) Clients & Chief Risk / Compliance Officers (CRO).
* **Core Job-To-Be-Done**:  
  > *"When market volatility occurs during an HNI client consultation, I want to instantly synthesize the client's multi-product portfolio against real-time market data and regulatory rules, so that I can deliver tailored, compliant investment proposals on the call without losing conversational momentum or incurring administrative overhead."*
* **The Workflow Friction**: RMs operate across 5–7 disconnected systems (Core Banking, CRM, FNZ Wealth, Bloomberg terminals), which increases manual data aggregation time during client calls.
* **The Compliance Friction**: Passing unmasked client PII to foreign-hosted LLMs violates the DPDP Act 2023 and RBI data localization mandates.


---

## 3. UI/UX Abstraction Layer (The RM Interface)

The UI must act as an abstraction layer. To maintain the "Match between system and the real world" heuristic, backend engineering states are translated entirely into banking taxonomy. Exposing tech fluency (e.g., LangGraph, MCP, Vector Search) to a non-tech user degrades trust and increases cognitive friction.

### Engineering State to RM UX Translation

| Engineering State (Backend) | Flawed UX Copy (Tech Jargon) | Corrected UX Copy (RM Terminology) |
| :--- | :--- | :--- |
| **Supervisor Node Routing** | Routing query to Portfolio Agent... | Analyzing client request... |
| **MCP Tool Execution** | MCP Tool 'get_portfolio' active... | Retrieving current asset allocation... |
| **RAG Vector Search** | Querying Qdrant for nearest neighbor... | Cross-referencing SEBI compliance guidelines... |
| **LLM Inference** | Sarvam-105B synthesizing response... | Drafting investment proposal... |
| **LangGraph NodeInterrupt** | NodeInterrupt: Awaiting human override. | Action Required: Review and approve proposal. |
| **DPDP Masking Middleware** | PII tokenized before LLM context injection. | Client privacy mask active. |

### Refined UX Principles for the RM Persona
1. **Outcome-Oriented Status Indicators**: Instead of showing what the software is doing (e.g., "Running multi-agent sub-graph"), the UI shows what business value is being generated (e.g., "Calculating 5-year SIP performance").
2. **Familiar Action Verbs**: Interface copy relies on verbs RMs use daily: Reviewing, Calculating, Cross-referencing, Drafting, Verifying.
3. **The "Glanceable" Dashboard**: During high-volume outbound calls, data is presented using standard financial typography (green/red yields, localized INR formatting) rather than raw AI JSON outputs.

### The "Client Context" Sidebar (Zero Toggling)
To ensure the RM never has to switch tabs during a live consultation, the following data fields are permanently pinned to the right-hand sidebar on page load:

1. **The Core Identity**: Client Name, Tier (e.g., Private Wealth Tier 1), and KYC Status.
2. **Portfolio Health**: Total Current AUM (₹), Unrealized P&L (+/-%), and Risk Appetite Score (e.g., Aggressive).
3. **Allocation & Liquidity**: Current Asset Mix (Equity/Debt/Cash ratio) and Total Monthly SIP Inflow.
4. **Actionable Intelligence**: Next Important Date (e.g., SIP Renewal, Tax Harvesting) and Recent Interaction notes.

---

## 4. Infrastructure & Hardware Sizing Strategy

### 🖥️ Hardware Capacity & Feasibility Analysis

| Model | Model Size / Parameters | Minimum VRAM / RAM (Quantized Q4) | Local Workstation Feasibility (16GB RAM, Integrated GPU) | Production On-Premise Sizing |
| :--- | :--- | :--- | :--- | :--- |
| **Sarvam-30B** | 30B MoE (~2.4B active) | ~16–20 GB VRAM | **Infeasible** (Requires dedicated GPU VRAM) | 1x NVIDIA L40S / A10G (24–48GB VRAM) |
| **Sarvam-105B** | 105B MoE (~10.3B active) | ~55–60 GB VRAM | **Infeasible** (Triggers OOM crash) | 2x NVIDIA A100 / H100 (80GB VRAM) |

> [!NOTE]
> Standard developer workstations (e.g., 16GB RAM, integrated graphics) lack the dedicated VRAM required to host 30B or 105B open-weights models locally. 

### 🌐 Hybrid Deployment Architecture (PoC vs. Production)

1. **Phase 1 PoC / Development Tier (Sarvam Cloud API)**:
   * **Inference Endpoint**: [Sarvam AI Cloud REST API](https://www.sarvam.ai/) (`https://api.sarvam.ai/v1`).
   * **Free Tier Capability**: ₹100 worth of free universal sign-up credits (plus up to ₹300 bonus credits on Starter plan activation).
   * **PoC Cost Efficiency**: 
     * `Sarvam-30B`: ₹2.5 / 1M input tokens, ₹10 / 1M output tokens.
     * `Sarvam-105B`: ₹4.0 / 1M input tokens, ₹16 / 1M output tokens.
   * **PoC Masking**: Client PII is tokenized/anonymized at the local MCP layer before sending payloads to the Sarvam API endpoint.

2. **Phase 2 Production Tier (Sovereign On-Premise VPC)**:
   * **Inference Endpoint**: vLLM / Ollama multi-GPU cluster deployed inside an India-based Virtual Private Cloud (AWS Mumbai / Azure India VPC).
   * **Data Sovereignty**: Open-weights Sarvam models run 100% on-premise within the bank's sovereign perimeter.

---

## 5. System Architecture & Tech Stack

| Layer | Technology | Engineering Rationale & OEM Specifications |
| :--- | :--- | :--- |
| **Reasoning Model** | Sarvam-105B | Flagship 105B Mixture-of-Experts (MoE) model (~10.3B active parameters/token, 128K context window). Deployed via Sarvam Cloud API for PoC, and on-premise vLLM for Production. |
| **Routing Model** | Sarvam-30B | Ultra-fast 30B parameter MoE model (~2.4B active parameters/token, 65K context window). Optimized for low-latency graph routing. |
| **Orchestration** | LangGraph (Python) | Models the multi-agent system as a stateful, cyclic directed graph. Employs `langgraph-checkpoint-postgres` for persistent PostgreSQL checkpointing. |
| **Integration** | Model Context Protocol (MCP) | Anthropic / Linux Foundation open standard isolating LLMs from banking infrastructure, enforcing middleware PII tokenization. |
| **Retrieval** | Qdrant Cloud | Vector database for embedding and retrieving SEBI-approved research documents. |
| **Database** | Supabase (PostgreSQL) | Handles RM authentication, state persistence, and hosts wealth management tables (Clients, Portfolios, Assets). |

---

## 6. Core Multi-Agent Workflows

The platform utilizes a Deterministic Orchestrator Pattern to manage complex financial reasoning.

> ⚠️ **PoC vs. Production LLM Strategy (The Cloud vs. Sovereign Trade-off)**
> * **The PoC (Current Phase)**: We are using the **Groq API (`llama-3.3-70b-versatile`)** to simulate the routing and reasoning nodes. 
>   * *Pros*: Zero infrastructure overhead, ultra-low latency, enables immediate end-to-end testing of the LangGraph/MCP architecture.
>   * *Cons*: Relies on an external cloud endpoint, which is strictly prohibited for actual banking data under DPDP Act rules.
> * **The Production Phase**: Will completely sever ties with cloud endpoints and transition to **Sovereign On-Premise Open-Weights (Sarvam/Llama)** running inside a secure, air-gapped Bank VPC.
>   * *Pros*: 100% Data Localization, zero risk of data leakage, full regulatory compliance.
>   * *Cons*: Requires significant CapEx for local GPU hardware (A100/H100 clusters) and introduces higher inference latency.

* **The Supervisor Node**: Powered by Sarvam-30B, this node receives the RM’s natural language query, classifies the intent, and routes execution to specialist subgraphs.
* **The Portfolio Agent**: Powered by Sarvam-105B, this agent connects securely to the Supabase database via an MCP tool (`get_client_portfolio()`, `calculate_sip_return()`) to retrieve client asset allocations, calculate SIP performance metrics, and model multi-product adoptions.
* **The Research & Compliance Agent**: Cross-references proposed financial advice against the Qdrant vector database to ensure logic is mathematically sound, regulatory compliant, and auditable.

---

## 7. Regulatory Guardrails (Programmatic Compliance)

* **RBI MRMF (Kill Switch & Governance)**: Adheres to **RBI Draft Guidance on MRMF (Press Release No. 2026-2027/528, June 24, 2026)**. System utilizes conditional interrupt edges (`interrupt_before=["human_review"]`). Before finalizing proposals or emails, the graph halts, surfacing reasoning to the RM for logged validation. Audit logs retained for 10 years.
* **SEBI Cyber Resilience & CSCRF**: Complies with **SEBI Advisory Circular HO/13/19/12(1)2026-ITD-1_CIMGI/10873/2026 (May 5, 2026)** under `cyber-suraksha.ai`. Deploys autonomous API vulnerability monitoring, OWASP Top 10 hardening, and SBOM enforcement.
* **DPDP Act 2023 (Data Scrubbing)**: MCP intermediary tools scrub and tokenize Personally Identifiable Information (PII) before payloads are transmitted to the LLM endpoint.

---

## 8. Engineering Implementation: LangGraph + MCP + Sarvam Code Spec

Below is the updated Python blueprint for the Supervisor node, configured to support both the **Sarvam Cloud API (PoC Tier)** and **On-Premise vLLM (Production Tier)**.

```python
import os
from typing import Annotated, Literal
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.postgres import PostgresSaver
from langchain_openai import ChatOpenAI  # Works with Sarvam AI API & local vLLM OpenAI-compatible endpoints

# 1. Define the Stateful Memory Object
class AgentState(TypedDict):
    messages: Annotated[list, "The message history"]
    next_node: str  # The routing destination
    requires_approval: bool  # The RBI MRMF Interrupt Flag

# 2. Initialize Sarvam Model (Cloud API for PoC / Local vLLM for Production)
# Sarvam AI API endpoints are OpenAI-compatible
SARVAM_API_KEY = os.getenv("SARVAM_API_KEY", "your-free-tier-api-key")
SARVAM_BASE_URL = os.getenv("SARVAM_BASE_URL", "https://api.sarvam.ai/v1")

local_router_llm = ChatOpenAI(
    model="sarvam-30b",
    api_key=SARVAM_API_KEY,
    base_url=SARVAM_BASE_URL,
    temperature=0.1
)

# 3. Define Supervisor Node Logic
def supervisor_node(state: AgentState):
    """
    Evaluates the RM's query and routes to the appropriate specialist agent.
    """
    messages = state["messages"]
    system_prompt = (
        "You are the Supervisor for Pramiti OS. Analyze the Relationship Manager's request. "
        "Route to 'portfolio_agent' if the query involves asset allocation or SIP returns. "
        "Route to 'compliance_agent' if the query involves SEBI guidelines or risk checking. "
        "Respond ONLY with the exact name of the routing destination."
    )
    
    response = local_router_llm.invoke([{"role": "system", "content": system_prompt}] + messages)
    destination = response.content.strip().lower()
    return {"next_node": destination}

# 4. Define Node Interrupt Edge (The RBI Kill Switch)
def check_approval(state: AgentState):
    if state.get("requires_approval"):
        return "human_review"
    return END

# 5. Build the Cyclic Graph
workflow = StateGraph(AgentState)

workflow.add_node("supervisor", supervisor_node)
workflow.add_node("portfolio_agent", portfolio_agent_node)
workflow.add_node("compliance_agent", compliance_agent_node)
workflow.add_node("human_review", human_review_node)

workflow.set_entry_point("supervisor")

workflow.add_conditional_edges(
    "supervisor",
    lambda x: x["next_node"],
    {
        "portfolio_agent": "portfolio_agent",
        "compliance_agent": "compliance_agent"
    }
)

workflow.add_conditional_edges("portfolio_agent", check_approval)
workflow.add_conditional_edges("compliance_agent", check_approval)

# 6. Compile with Persistent PostgreSQL Checkpointer (langgraph-checkpoint-postgres)
DB_URI = os.getenv("POSTGRES_URI", "postgresql://postgres:password@localhost:5432/pramiti_db")

with PostgresSaver.from_conn_string(DB_URI) as checkpointer:
    checkpointer.setup()
    app = workflow.compile(
        checkpointer=checkpointer,
        interrupt_before=["human_review"]  # Programmatic RBI Kill Switch trigger
    )
```

---

## 9. Phase 1 MVP Scope (Acceptance Criteria)

* **Epic 1: API & Infrastructure Setup**. Register on Sarvam AI Developer Dashboard to claim the **₹100 free credit tier**. Set up environment variables (`SARVAM_API_KEY`). Initialize Supabase PostgreSQL with mock data for 5-10 HNI clients.
* **Epic 2: MCP Tool Creation**. Build two functional Python-based MCP servers: `get_client_portfolio()` and `calculate_sip_return()`. Scrub PII client names before passing data to the LLM.
* **Epic 3: Graph Construction**. Implement LangGraph routing logic using `ChatOpenAI(base_url="https://api.sarvam.ai/v1")`. Prove multi-turn state persistence with `langgraph-checkpoint-postgres`.
* **Epic 4: Compliance Validation**. Demonstrate `interrupt_before=["human_review"]` functionality, pausing graph execution for explicit RM approval.
