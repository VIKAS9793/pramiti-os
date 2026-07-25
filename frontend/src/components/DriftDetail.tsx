import React from 'react';
import styles from '../app/page.module.css';
import { Card } from './Card';
import { Button } from './Button';
import { StatusPill } from './StatusPill';

interface DriftDetailProps {
  selectedClient: string;
  setViewMode: (mode: 'slider_drawer') => void;
  handleSend: (overrideValue?: string) => void;
}

/**
 * Renders the deep-dive view for portfolio drift analysis.
 *
 * Displays visual indicators of asset allocation deviations against client mandates, 
 * highlighting specific out-of-bounds metrics (e.g., equity overweight) and providing 
 * quick actions to resolve them.
 *
 * @param {DriftDetailProps} props - The component props.
 * @param {string} props.selectedClient - The currently active client context.
 * @param {function} props.setViewMode - Callback to navigate to the slider adjustment view.
 * @param {function} props.handleSend - Callback to trigger an automated LLM proposal generation.
 * @returns {JSX.Element} The rendered Drift Detail interface.
 */
export function DriftDetail({ selectedClient, setViewMode, handleSend }: DriftDetailProps) {
  return (
    <div className={styles.driftView}>
      <div className={styles.contextStrip}>
        Reviewing: {selectedClient} — Equity 15% overweight — started 3 min ago
      </div>
      
      <div className={styles.driftHeader}>
        <div>
          <h2>Portfolio Off-Target — {selectedClient}</h2>
          <p>Private Wealth Tier 1 · Total AUM: <strong>₹1.24 Cr</strong></p>
        </div>
      </div>

      <div className={styles.insightBox}>
        <div className={styles.insightIcon}>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><circle cx="12" cy="12" r="10"/><path d="M12 8v4M12 16h.01"/></svg>
        </div>
        <div>
          Equity outperformance over 90 days has pushed allocation past the Aggressive Mandate threshold. Review required.
        </div>
      </div>

      <Card title="Allocation Drift">
        <div className={styles.driftBarRow}>
          <div className={styles.driftLabel}>
            <span>
              <strong>Equity</strong>
              <span className={styles.driftLabelMeta}>Target 50% · Current 65%</span>
            </span>
            <StatusPill severity="amber">+15% overweight</StatusPill>
          </div>
          <div className={styles.progressTrack}>
            <div className={styles.progressFillAmber} style={{ width: "65%" }}></div>
            <div className={styles.targetIndicator} style={{ left: "50%" }} title="Target: 50%"></div>
          </div>
        </div>

        <div className={styles.driftBarRow}>
          <div className={styles.driftLabel}>
            <span>
              <strong>Debt</strong>
              <span className={styles.driftLabelMeta}>Target 40% · Current 25%</span>
            </span>
            <StatusPill severity="blue">−15% underweight</StatusPill>
          </div>
          <div className={styles.progressTrack}>
            <div className={styles.progressFillBlue} style={{ width: "25%" }}></div>
            <div className={styles.targetIndicator} style={{ left: "40%" }} title="Target: 40%"></div>
          </div>
        </div>

        <div className={styles.driftBarRow}>
          <div className={styles.driftLabel}>
            <span>
              <strong>Cash</strong>
              <span className={styles.driftLabelMeta}>Target 10% · Current 10%</span>
            </span>
            <StatusPill severity="green">On target</StatusPill>
          </div>
          <div className={styles.progressTrack}>
            <div className={styles.progressFillGreen} style={{ width: "10%" }}></div>
            <div className={styles.targetIndicator} style={{ left: "10%" }} title="Target: 10%"></div>
          </div>
        </div>

        <div className={styles.recommendationBanner}>
          <strong>Suggested Action:</strong> Reallocate <strong>₹10,00,000 (₹10.00 Lakh)</strong> from Equity to Debt.
        </div>

        <div className={styles.driftActionRow}>
          <Button variant="primary-large" onClick={() => setViewMode('slider_drawer')}>
            ⚡ Adjust Rebalancing Amount
          </Button>
          <Button variant="secondary-large" onClick={() => handleSend("Reallocate 10 Lakhs from Equity to Debt")}>
            💬 Open Copilot to Execute
          </Button>
        </div>
      </Card>
    </div>
  );
}
