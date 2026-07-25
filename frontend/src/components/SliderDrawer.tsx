import React from 'react';
import styles from '../app/page.module.css';
import { Card } from './Card';
import { Button } from './Button';

interface SliderDrawerProps {
  selectedClient: string;
  rebalanceAmount: number;
  setRebalanceAmount: (val: number) => void;
  newEquityPct: string;
  newDebtPct: string;
  isSebiCompliant: boolean;
  isRbiCompliant: boolean;
  setViewMode: (mode: 'drift_detail') => void;
  setIsCommitted: (val: boolean) => void;
  handleSend: (overrideValue?: string) => void;
}

/**
 * Renders an interactive slider for fine-tuning portfolio reallocation amounts.
 *
 * Provides real-time preview of the resulting portfolio mix (Equity/Debt) and 
 * synchronously checks compliance against SEBI rules and RBI limits before 
 * allowing the RM to confirm the trade.
 *
 * @param {SliderDrawerProps} props - The component props.
 * @param {string} props.selectedClient - The currently active client context.
 * @param {number} props.rebalanceAmount - The current numerical value of the slider.
 * @param {function} props.setRebalanceAmount - Callback to update the slider state.
 * @param {string} props.newEquityPct - The calculated post-trade equity percentage.
 * @param {string} props.newDebtPct - The calculated post-trade debt percentage.
 * @param {boolean} props.isSebiCompliant - Flag indicating if the simulated state passes SEBI rules.
 * @param {boolean} props.isRbiCompliant - Flag indicating if the simulated trade volume passes RBI limits.
 * @param {function} props.setViewMode - Callback to navigate back to the drift detail view.
 * @param {function} props.setIsCommitted - Callback to mark the trade as committed.
 * @param {function} props.handleSend - Callback to trigger the final execution workflow.
 * @returns {JSX.Element} The rendered Slider Drawer interface.
 */
export function SliderDrawer({
  selectedClient,
  rebalanceAmount,
  setRebalanceAmount,
  newEquityPct,
  newDebtPct,
  isSebiCompliant,
  isRbiCompliant,
  setViewMode,
  setIsCommitted,
  handleSend
}: SliderDrawerProps) {
  return (
    <div className={styles.sliderView}>
      <div className={styles.contextStrip}>
        Reviewing: {selectedClient} — Equity 15% overweight — started 3 min ago
      </div>

      <div className={styles.driftHeader}>
        <div>
          <h2>Adjust Rebalancing</h2>
          <p>Fine-tune proposed weights before committing.</p>
        </div>
      </div>

      <Card>
        <div className={styles.sliderControlGroup}>
          <div className={styles.sliderHeader}>
            <span className={styles.sliderLabel}>Reallocation Amount</span>
            <span className={styles.sliderValueBadge}>₹{(rebalanceAmount / 100000).toFixed(2)} Lakh</span>
          </div>

          <input 
            type="range" 
            min={100000} 
            max={3000000} 
            step={50000}
            value={rebalanceAmount} 
            onChange={(e) => setRebalanceAmount(Number(e.target.value))}
            className={styles.rangeSlider}
          />

          <div className={styles.sliderRangeLabels}>
            <span>Min: ₹1.00 Lakh</span>
            <span>Max: ₹30.00 Lakh</span>
          </div>

          <div className={styles.inputSyncRow}>
            <span className={styles.inputSyncLabel}>Manual value (₹ INR)</span>
            <input 
              type="number" 
              value={rebalanceAmount} 
              onChange={(e) => setRebalanceAmount(Number(e.target.value))}
              className={styles.numberInput}
            />
          </div>
        </div>

        {/* Simulated Shift Preview */}
        <div className={styles.simulationPreview}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <h4>What This Looks Like</h4>
            <span style={{ fontSize: '0.7rem', padding: '2px 8px', background: 'rgba(37, 99, 235, 0.2)', border: '1px solid rgba(37, 99, 235, 0.4)', borderRadius: '4px', color: '#CBD5E1', textTransform: 'uppercase' }}>
              Preview — Not Yet Executed
            </span>
          </div>
          <div className={styles.simRow}>
            <span>Equity Shift:</span>
            <span>[ 65.0% ] ═════════► [ <strong>{newEquityPct}%</strong> ] (Target: 50.0%)</span>
          </div>
          <div className={styles.simRow}>
            <span>Debt Shift:</span>
            <span>[ 25.0% ] ═════════► [ <strong>{newDebtPct}%</strong> ] (Target: 40.0%)</span>
          </div>
        </div>

        {/* Live Compliance Status */}
        <div className={styles.complianceStatusBox}>
          <h4>Compliance</h4>
          <div className={styles.complianceBadges}>
            <span className={isSebiCompliant ? styles.tagGreen : styles.tagRed}>
              SEBI Rule 101: {isSebiCompliant ? "Cleared" : "Violation — equity below 30%"}
            </span>
            <span className={isRbiCompliant ? styles.tagGreen : styles.tagRed}>
              RBI Guideline 42: {isRbiCompliant ? "Cleared" : "Violation — exceeds ₹5 Cr"}
            </span>
          </div>
        </div>

        {/* Drawer Actions */}
        <div className={styles.drawerActions}>
          <Button variant="secondary-large" onClick={() => setViewMode('drift_detail')}>
            ❌ Cancel
          </Button>
          <div className={styles.actionConfirmWrapper}>
            {isSebiCompliant && isRbiCompliant && (
              <div className={styles.approvalHeadline}>
                ✅ No manager approval needed — you can proceed
              </div>
            )}
            <Button 
              variant="primary-large" 
              disabled={!isSebiCompliant || !isRbiCompliant}
              onClick={() => {
                setIsCommitted(true);
                // Log immutable state snapshot
                const snapshot = {
                  action: "Confirm Rebalancing",
                  client: selectedClient,
                  amount: rebalanceAmount,
                  timestamp: new Date().toISOString(),
                  compliance: {
                    sebi: isSebiCompliant,
                    rbi: isRbiCompliant
                  },
                  uiStateShown: {
                    newEquityPct,
                    newDebtPct
                  }
                };
                console.log("[AUDIT LOG] Immutable state capture:", snapshot);
                
                handleSend(`Execute rebalancing of ₹${(rebalanceAmount / 100000).toFixed(2)} Lakh from Equity to Debt for ${selectedClient}`);
              }}
            >
              ⚡ Confirm Rebalancing
            </Button>
          </div>
        </div>
      </Card>
    </div>
  );
}
