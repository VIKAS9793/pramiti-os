"use client";

import { useState } from "react";
import styles from "./page.module.css";
import { CockpitView } from "../components/CockpitView";
import { DriftDetail } from "../components/DriftDetail";
import { SliderDrawer } from "../components/SliderDrawer";
import { ChatCopilot } from "../components/ChatCopilot";

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

  // Dynamic calculations based on slider (Total AUM: 1.24 Cr = 12,40,00,000 / 1.24 Cr = 124 Lakhs)
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
        headers: { "Content-Type": "application/json" },
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
             return { ...msg, content: "⚠️ System degraded. API bridge on port 8000 is unreachable. Please contact IT support." };
          }
          return msg;
       }));
       setRequiresApproval(true); // Lock further actions during degradation until cleared manually or re-fetched.
    } finally {
      setIsProcessing(false);
    }
  };

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
            inputValue={inputValue}
            setInputValue={setInputValue}
            isProcessing={isProcessing}
            requiresApproval={requiresApproval}
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
                <div className={styles.clientTier}>Private Wealth Tier 1</div>
              </div>
            </div>
          </div>

          {/* Portfolio Health Widget */}
          <div className={styles.widget}>
            <div className={styles.widgetTitle}>Portfolio Health</div>
            <div className={styles.statRow}>
              <span className={styles.statLabel}>Total AUM</span>
              <span className={styles.statValue}>₹1.24 Cr</span>
            </div>
            <div className={styles.statRow}>
              <span className={styles.statLabel}>Unrealized P&L</span>
              <span className={`${styles.statValue} ${styles.positive}`}>+14.2%</span>
            </div>
            <div className={styles.statRow}>
              <span className={styles.statLabel}>Risk Appetite</span>
              <span className={styles.statValue}>Aggressive</span>
            </div>
          </div>

          {/* Allocation Widget */}
          <div className={styles.widget}>
            <div className={styles.widgetTitle}>Asset Mix</div>
            <div className={styles.allocationBar}>
              <div className={styles.allocEquity} style={{ width: '65%' }} title="Equity: 65%"></div>
              <div className={styles.allocDebt} style={{ width: '25%' }} title="Debt: 25%"></div>
              <div className={styles.allocCash} style={{ width: '10%' }} title="Cash: 10%"></div>
            </div>
            <div className={styles.allocLegend}>
              <div><span className={styles.legendDot} style={{background: 'var(--accent)'}}></span>Equity</div>
              <div><span className={styles.legendDot} style={{background: 'var(--accent-border)'}}></span>Debt</div>
              <div><span className={styles.legendDot} style={{background: 'var(--border-muted)'}}></span>Cash</div>
            </div>
          </div>

          {/* Actionable Info Widget */}
          <div className={styles.widget}>
            <div className={styles.widgetTitle}>Next Actions</div>
            <div className={styles.statRow}>
              <span className={styles.statLabel}>Next SIP Date</span>
              <span className={styles.statValue}>05 Aug 2026</span>
            </div>
            <div className={styles.statRow}>
              <span className={styles.statLabel}>Monthly Inflow</span>
              <span className={styles.statValue}>₹75,000</span>
            </div>
          </div>
        </div>
      </aside>
    </div>
  );
}
