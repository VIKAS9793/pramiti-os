"use client";

import { useState } from "react";
import styles from "./page.module.css";
import { CockpitView } from "../components/CockpitView";
import { DriftDetail } from "../components/DriftDetail";
import { SliderDrawer } from "../components/SliderDrawer";
import { ChatCopilot } from "../components/ChatCopilot";

const clientDataMap: Record<string, any> = {
  "Aarav Sharma": {
    aum: "₹4.85 Cr",
    pnl: "+14.9%",
    pnlClass: styles.positive,
    risk: "Moderate-Aggressive",
    tier: "Private Wealth Tier 1",
    equity: 65,
    debt: 25,
    cash: 5,
    alts: 5,
    nextActionDate: "05 Aug 2026",
    monthlyInflow: "₹1,00,000"
  },
  "Priya Patel": {
    aum: "₹2.50 Cr",
    pnl: "+8.4%",
    pnlClass: styles.positive,
    risk: "Aggressive",
    tier: "Private Wealth Tier 2",
    equity: 70,
    debt: 0,
    cash: 30,
    alts: 0,
    nextActionDate: "12 Aug 2026",
    monthlyInflow: "₹50,000"
  },
  "Kabir Singh": {
    aum: "₹85.00 Lakh",
    pnl: "-2.1%",
    pnlClass: styles.negative,
    risk: "Moderate",
    tier: "Wealth",
    equity: 50,
    debt: 40,
    cash: 10,
    alts: 0,
    nextActionDate: "07 Aug 2026",
    monthlyInflow: "₹25,000"
  }
};

type ViewMode = "cockpit" | "drift_detail" | "slider_drawer" | "chat";

export type Message = {
  id: string;
  role: "rm" | "system";
  content: string;
  isProposal?: boolean;
};

/**
 * Main Interface Component for Pramiti OS Relationship Manager (RM).
 *
 * This component manages the global state for the RM workspace, handling navigation 
 * between different views (Cockpit, Drift Detail, Rebalance Slider, and Chat). 
 * It also manages the SSE (Server-Sent Events) connection to the backend LLM orchestrator.
 *
 * @returns {JSX.Element} The rendered RM interface.
 */
export default function PramitiRMInterface() {
  const [viewMode, setViewMode] = useState<ViewMode>("cockpit");
  const [selectedClient, setSelectedClient] = useState<string>("Aarav Sharma");
  
  // Interactive Slider State
  const [rebalanceAmount, setRebalanceAmount] = useState<number>(1000000); // 10 Lakhs in INR
  const [isCommitted, setIsCommitted] = useState<boolean>(false);

  // Chat State
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "init",
      role: "system",
      content: "Pramiti OS initialized. Secure session active. How can I assist you with the portfolio today?",
    },
  ]);
  const [inputValue, setInputValue] = useState("");
  const [isProcessing, setIsProcessing] = useState(false);
  const [requiresApproval, setRequiresApproval] = useState(false);

  // Dynamic calculations based on slider (AUM: 1.24 Cr = 12,40,00,000 / 1.24 Cr = 124 Lakhs)
  const totalAumLakhs = 124;
  const currentEquityLakhs = 80.6;
  const currentDebtLakhs = 31;
  const rebalanceLakhs = rebalanceAmount / 100000;

  const newEquityLakhs = currentEquityLakhs - rebalanceLakhs;
  const newDebtLakhs = currentDebtLakhs + rebalanceLakhs;
  const newEquityPct = ((newEquityLakhs / totalAumLakhs) * 100).toFixed(1);
  const newDebtPct = ((newDebtLakhs / totalAumLakhs) * 100).toFixed(1);

  const isSebiCompliant = parseFloat(newEquityPct) >= 30.0;
  const isRbiCompliant = rebalanceAmount <= 50000000; // <= 5 Cr

  // Chat API Call
  const handleSend = async (overrideValue?: string) => {
    const textToSend = overrideValue || inputValue;
    if (!textToSend.trim()) return;

    setViewMode("chat");
    const rmMsg: Message = { id: Date.now().toString(), role: "rm", content: textToSend };
    setMessages((prev) => [...prev, rmMsg]);
    if (!overrideValue) setInputValue("");
    setIsProcessing(true);
    setRequiresApproval(false);
    
    const sysMsgId = "sys-" + Date.now().toString();
    setMessages((prev) => [...prev, { id: sysMsgId, role: "system", content: "..." }]);

    try {
      const response = await fetch("http://localhost:8000/chat/stream", {
        method: "POST",
        headers: { 
          "Content-Type": "application/json",
          "Authorization": `Bearer ${process.env.NEXT_PUBLIC_DEV_API_TOKEN || ""}`
        },
        body: JSON.stringify({ message: rmMsg.content }),
      });

      if (!response.ok) throw new Error("API Bridge failed");

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      let done = false;
      
      while (reader && !done) {
        const { value, done: readerDone } = await reader.read();
        done = readerDone;
        if (value) {
          const chunk = decoder.decode(value);
          const lines = chunk.split("\n");
          for (let line of lines) {
             if (line.startsWith("data: ")) {
                try {
                  const dataStr = line.substring(6);
                  const data = JSON.parse(dataStr);
                  setMessages((prev) => prev.map(msg => {
                    if (msg.id === sysMsgId) {
                       return {
                         ...msg,
                         content: data.content,
                         isProposal: data.requires_approval
                       };
                    }
                    return msg;
                  }));
                  if (data.requires_approval) setRequiresApproval(true);
                } catch (e) {
                   console.error("SSE parse error", e);
                }
             }
          }
        }
      }
    } catch (error) {
       console.error("Chat error:", error);
       setMessages((prev) => prev.map(msg => {
          if (msg.id === sysMsgId) {
             return { ...msg, content: "⚠️ Portfolio calculation engine is briefly offline. Re-trying in 10s... (Error Code: PRM-8000)" };
          }
          return msg;
       }));
       setRequiresApproval(true); // Lock further actions during degradation until cleared manually or re-fetched.
    } finally {
      setIsProcessing(false);
    }
  };

  const currentClientData = clientDataMap[selectedClient] || clientDataMap["Aarav Sharma"];

  return (
    <div className={styles.container}>
      {/* Primary Workspace */}
      <main className={styles.workspace}>
        {/* Navigation Bar */}
        <header className={styles.header}>
          <div className={styles.headerTitle}>
            <h1>⚡ PRAMITI OS</h1>
            <span className={styles.headerSub}>Wealth Command Centre</span>
          </div>
          <div className={styles.navTabs}>
            <button 
              className={`${styles.tabBtn} ${viewMode === 'cockpit' ? styles.activeTab : ''}`} 
              onClick={() => setViewMode('cockpit')}
            >
              My Day
            </button>
            <button 
              className={`${styles.tabBtn} ${viewMode === 'drift_detail' ? styles.activeTab : ''}`} 
              onClick={() => setViewMode('drift_detail')}
            >
              Client Review
            </button>
            <button 
              className={`${styles.tabBtn} ${viewMode === 'slider_drawer' ? styles.activeTab : ''}`} 
              onClick={() => setViewMode('slider_drawer')}
            >
              Rebalance
            </button>
            <button 
              className={`${styles.tabBtn} ${viewMode === 'chat' ? styles.activeTab : ''}`} 
              onClick={() => setViewMode('chat')}
            >
              Ask Pramiti
            </button>
          </div>
        </header>

        {viewMode === 'cockpit' && (
          <CockpitView 
            setSelectedClient={setSelectedClient}
            setViewMode={setViewMode}
            setInputValue={setInputValue}
          />
        )}

        {viewMode === 'drift_detail' && (
          <DriftDetail 
            selectedClient={selectedClient}
            setViewMode={setViewMode}
            handleSend={handleSend}
          />
        )}

        {viewMode === 'slider_drawer' && (
          <SliderDrawer 
            selectedClient={selectedClient}
            rebalanceAmount={rebalanceAmount}
            setRebalanceAmount={setRebalanceAmount}
            newEquityPct={newEquityPct}
            newDebtPct={newDebtPct}
            isSebiCompliant={isSebiCompliant}
            isRbiCompliant={isRbiCompliant}
            setViewMode={setViewMode}
            setIsCommitted={setIsCommitted}
            handleSend={handleSend}
          />
        )}

        {viewMode === 'chat' && (
          <ChatCopilot 
            selectedClient={selectedClient}
            messages={messages}
            setMessages={setMessages}
            inputValue={inputValue}
            setInputValue={setInputValue}
            isProcessing={isProcessing}
            requiresApproval={requiresApproval}
            setRequiresApproval={setRequiresApproval}
            handleSend={handleSend}
            setViewMode={setViewMode}
          />
        )}
      </main>

      {/* Client Context Sidebar */}
      <aside className={styles.sidebar}>
        <div className={styles.sidebarHeader}>Client</div>
        <div className={styles.sidebarContent}>
          {/* Identity Widget */}
          <div className={styles.widget}>
            <div className={styles.clientIdentity}>
              <div className={styles.avatar}>
                {selectedClient.split(' ').map(n => n[0]).join('').substring(0,2).toUpperCase()}
              </div>
              <div>
                <div className={styles.clientName}>{selectedClient}</div>
                <div className={styles.clientTier}>{currentClientData.tier}</div>
              </div>
            </div>
          </div>

          {/* Portfolio Health Widget */}
          <div className={styles.widget}>
            <div className={styles.widgetTitle}>Portfolio Health</div>
            <div className={styles.statRow}>
              <span className={styles.statLabel}>Assets Under Management (AUM)</span>
              <span className={styles.statValue}>{currentClientData.aum}</span>
            </div>
            <div className={styles.statRow}>
              <span className={styles.statLabel}>Unrealized P&L</span>
              <span className={`${styles.statValue} ${currentClientData.pnlClass || ''}`}>{currentClientData.pnl}</span>
            </div>
            <div className={styles.statRow}>
              <span className={styles.statLabel}>Risk Appetite</span>
              <span className={styles.statValue}>{currentClientData.risk}</span>
            </div>
          </div>

          {/* Allocation Widget */}
          <div className={styles.widget}>
            <div className={styles.widgetTitle}>Asset Mix</div>
            <div className={styles.allocationBar}>
              {currentClientData.equity > 0 && <div className={styles.allocEquity} style={{ width: `${currentClientData.equity}%` }} title={`Equity: ${currentClientData.equity}%`}></div>}
              {currentClientData.debt > 0 && <div className={styles.allocDebt} style={{ width: `${currentClientData.debt}%` }} title={`Debt: ${currentClientData.debt}%`}></div>}
              {currentClientData.cash > 0 && <div className={styles.allocCash} style={{ width: `${currentClientData.cash}%` }} title={`Cash: ${currentClientData.cash}%`}></div>}
              {currentClientData.alts > 0 && <div className={styles.allocAlts} style={{ width: `${currentClientData.alts}%`, background: '#8b5cf6' }} title={`Alts: ${currentClientData.alts}%`}></div>}
            </div>
            <div className={styles.allocLegend}>
              <div><span className={styles.legendDot} style={{background: 'var(--accent)'}}></span>Equity</div>
              <div><span className={styles.legendDot} style={{background: 'var(--accent-border)'}}></span>Debt</div>
              <div><span className={styles.legendDot} style={{background: 'var(--border-muted)'}}></span>Cash</div>
              {currentClientData.alts > 0 && <div><span className={styles.legendDot} style={{background: '#8b5cf6'}}></span>Alts</div>}
            </div>
          </div>

          {/* Actionable Info Widget */}
          <div className={styles.widget}>
            <div className={styles.widgetTitle}>Next Actions</div>
            <div className={styles.statRow}>
              <span className={styles.statLabel}>Next SIP Date</span>
              <span className={styles.statValue}>{currentClientData.nextActionDate}</span>
            </div>
            <div className={styles.statRow}>
              <span className={styles.statLabel}>Monthly Inflow</span>
              <span className={styles.statValue}>{currentClientData.monthlyInflow}</span>
            </div>
          </div>
        </div>
      </aside>
    </div>
  );
}
