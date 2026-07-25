import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeRaw from 'rehype-raw';
import styles from '../app/page.module.css';
import { Button } from './Button';
import { StatusPill } from './StatusPill';

interface Message {
  id: string;
  role: 'rm' | 'system';
  content: string;
  isProposal?: boolean;
}

interface ChatCopilotProps {
  selectedClient: string;
  messages: Message[];
  setMessages: (updater: (prev: Message[]) => Message[]) => void;
  inputValue: string;
  setInputValue: (val: string) => void;
  isProcessing: boolean;
  requiresApproval: boolean;
  setRequiresApproval: (val: boolean) => void;
  handleSend: (msg?: string) => void;
  setViewMode: (mode: 'cockpit' | 'drift_detail' | 'slider_drawer' | 'chat') => void;
}

/**
 * Renders the AI Copilot chat interface for the Relationship Manager.
 *
 * Handles rendering the conversation history, processing dynamic compliance 
 * verdicts via `<compliance_verdict>` tags, unmasking PII for the RM's view, 
 * and providing quick action chips.
 *
 * @param {ChatCopilotProps} props - The component props.
 * @param {string} props.selectedClient - The currently active client context.
 * @param {Message[]} props.messages - Array of chat messages.
 * @param {string} props.inputValue - Current text input value.
 * @param {function} props.setInputValue - Callback to update input state.
 * @param {boolean} props.isProcessing - Indicates if the LLM is currently generating a response.
 * @param {boolean} props.requiresApproval - Indicates if the workflow is paused for MRMF approval.
 * @param {function} props.handleSend - Callback to trigger message dispatch.
 * @param {function} props.setViewMode - Callback to navigate workspace views.
 * @returns {JSX.Element} The rendered Chat Copilot interface.
 */
export function ChatCopilot({
  selectedClient,
  messages,
  inputValue,
  setInputValue,
  isProcessing,
  requiresApproval,
  handleSend,
  setViewMode
}: ChatCopilotProps) {

  // Helper to extract JSON from <compliance_verdict>
  const parseComplianceVerdict = (content: string) => {
    let cleanContent = content;
    let payload = null;
    
    const verdictMatch = content.match(/<compliance_verdict>([\s\S]*?)<\/compliance_verdict>/);
    if (verdictMatch && verdictMatch[1]) {
      try {
        payload = JSON.parse(verdictMatch[1]);
        cleanContent = content.replace(/<compliance_verdict>[\s\S]*?<\/compliance_verdict>/, '');
      } catch (e) {
        console.error("Failed to parse compliance verdict JSON", e);
      }
    }

    // Unmask PII dynamically in the authenticated RM view
    // Assuming the backend masks "Aarav Sharma" as "A**** S*****" or similar
    // For a generic approach in the PoC, we replace asterisks patterns or the specific masked name
    cleanContent = cleanContent.replace(/A\*\*\*\* S\*\*\*\*\*/g, selectedClient);
    // Also handle possible bolded/italicized masked variants from the LLM
    cleanContent = cleanContent.replace(/\*\*A\*\*\*\* S\*\*\*\*\*\*\*/g, `**${selectedClient}**`);

    return { payload, cleanContent };
  };

  return (
    <div className={styles.chatContainer}>
      <div className={styles.contextStrip}>
        Client Context: {selectedClient} — {
          selectedClient === 'Aarav Sharma' ? 'Equity Allocation Breach (15% overweight)' :
          selectedClient === 'Priya Patel' ? '₹25.00 Lakh awaiting deployment' :
          selectedClient === 'Kabir Singh' ? 'SIP payment pending — auto-retry 07 Aug' :
          'Review Required'
        }
      </div>

      <div className={styles.actionChips}>
        <button className={styles.chip} onClick={() => handleSend(`Draft a rebalancing proposal for ${selectedClient}`)} disabled={requiresApproval || isProcessing}>
          ⚡ Draft Rebalancing Proposal
        </button>
        <button className={styles.chip} onClick={() => handleSend(`Generate a 3-bullet WhatsApp summary of the rebalancing plan for ${selectedClient}`)} disabled={requiresApproval || isProcessing}>
          ⚡ WhatsApp Summary
        </button>
        <button className={styles.chip} onClick={() => handleSend(`Generate a tax summary report for ${selectedClient}`)} disabled={requiresApproval || isProcessing}>
          ⚡ Generate Tax Summary
        </button>
      </div>

      <div className={styles.chatArea}>
        {messages.map((msg) => {
          const { payload, cleanContent } = parseComplianceVerdict(msg.content);

          return (
            <div
              key={msg.id}
              className={`${styles.message} ${
                msg.role === "rm" ? styles.rmMessage : styles.systemMessage
              } ${msg.isProposal ? styles.proposalWrapper : ""}`}
            >
              {msg.isProposal ? (
                <div className={styles.proposalCard}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                    <h3 style={{ margin: 0 }}>Review Required</h3>
                    <span style={{ fontSize: '0.65rem', padding: '2px 6px', background: 'rgba(37, 99, 235, 0.2)', border: '1px solid rgba(37, 99, 235, 0.4)', borderRadius: '4px', color: '#CBD5E1', textTransform: 'uppercase' }}>
                      Preview — Not Yet Executed
                    </span>
                  </div>
                  
                  <div className={styles.proposalContent}>
                    <ReactMarkdown remarkPlugins={[remarkGfm]} rehypePlugins={[rehypeRaw]}>{cleanContent}</ReactMarkdown>
                  </div>
                  
                  {payload && (
                    <div className={styles.complianceStatusBox} style={{ marginTop: '16px' }}>
                      <h4 style={{ marginBottom: '8px' }}>Compliance Rules Applied</h4>
                      <div className={styles.complianceBadges}>
                        {payload.is_compliant ? (
                          <StatusPill severity="green">✅ Cleared per SEBI/RBI — no manager approval required</StatusPill>
                        ) : (
                          <StatusPill severity="red">🔴 Action flagged — please review before proceeding</StatusPill>
                        )}
                        {payload.citations && payload.citations.map((cit: string, idx: number) => (
                          <StatusPill key={idx} severity="blue">Citation: {cit}</StatusPill>
                        ))}
                      </div>
                      {payload.explanation && (
                        <div style={{ marginTop: '12px', fontSize: '0.85rem', color: 'var(--text-secondary)', borderLeft: '2px solid var(--border-color)', paddingLeft: '8px' }}>
                          <strong>System Reasoning:</strong> {payload.explanation}
                        </div>
                      )}
                    </div>
                  )}

                  <div className={styles.proposalActions}>
                    <Button variant="primary-small" onClick={() => {
                      setRequiresApproval(false);
                      setMessages(prev => [...prev, {
                        id: Date.now().toString(),
                        role: 'system',
                        content: '✅ **RM Approval Recorded.** Executing trades to Core Banking System...'
                      }]);
                    }}>
                      Confirm & Execute
                    </Button>
                    <Button variant="secondary-small" onClick={() => {
                      setRequiresApproval(false);
                    }}>
                      Reject / Modify
                    </Button>
                    <Button variant="secondary-small" onClick={() => setViewMode('slider_drawer')}>
                      Adjust Amount
                    </Button>
                  </div>
                </div>
              ) : (
                <ReactMarkdown remarkPlugins={[remarkGfm]} rehypePlugins={[rehypeRaw]}>{cleanContent}</ReactMarkdown>
              )}
            </div>
          );
        })}

        {isProcessing && (
          <div className={`${styles.message} ${styles.systemMessage}`}>
             <div className={styles.skeletonBox} style={{ width: '100%', height: '100%', padding: '16px' }}>
               <div className={styles.skeletonTitle}></div>
               <div className={styles.skeletonText}></div>
               <div className={styles.skeletonText}></div>
               <div className={styles.skeletonText} style={{ width: '80%' }}></div>
               <div style={{ display: 'flex', gap: '8px', marginTop: '12px' }}>
                  <div className={styles.skeletonPill}></div>
                  <div className={styles.skeletonPill}></div>
               </div>
             </div>
          </div>
        )}
      </div>

      <div className={styles.inputPanel}>
        <div className={styles.inputWrapper}>
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSend()}
            placeholder="Select a quick action above, or type your query..."
            className={styles.input}
            disabled={isProcessing}
          />
          <button
            onClick={() => handleSend()}
            className={styles.sendBtn}
            disabled={isProcessing || !inputValue.trim()}
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
}
