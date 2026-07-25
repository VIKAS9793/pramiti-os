import React from 'react';
import styles from '../app/page.module.css';
import { Card } from './Card';
import { Button } from './Button';
import { StatusPill } from './StatusPill';

interface CockpitViewProps {
  setSelectedClient: (client: string) => void;
  setViewMode: (mode: 'cockpit' | 'drift_detail' | 'slider_drawer' | 'chat') => void;
  setInputValue: (val: string) => void;
  hasData?: boolean;
}

/**
 * Renders the primary dashboard (Cockpit) for the Relationship Manager.
 *
 * Displays a high-level overview of the book of business, schedule, market briefing, 
 * and specific clients requiring attention due to portfolio drift or pending actions.
 *
 * @param {CockpitViewProps} props - The component props.
 * @param {function} props.setSelectedClient - Callback to set the active client context.
 * @param {function} props.setViewMode - Callback to navigate between workspace modes.
 * @param {boolean} [props.hasData=true] - Toggles empty state for the dashboard.
 * @returns {JSX.Element} The rendered Cockpit dashboard.
 */
export function CockpitView({ setSelectedClient, setViewMode, setInputValue, hasData = true }: CockpitViewProps) {
  if (!hasData) {
    return (
      <div className={styles.cockpitView}>
        <div className={styles.welcomeBanner}>
          <div>
            <h2>Good Morning, Vikas 👋</h2>
            <p>Friday, 05 Aug 2026 | Book AUM: <strong>₹0.00</strong> (0 Active Folios / Demat Accounts)</p>
          </div>
        </div>
        <Card title="Actionable Client Triggers">
          <div className={styles.emptyState}>
            <div className={styles.emptyStateIcon}>🎉</div>
            <p>All client portfolios are within mandated thresholds.</p>
            <p>No action required.</p>
          </div>
        </Card>
      </div>
    );
  }

  return (
    <div className={styles.cockpitView}>
      <div className={styles.welcomeBanner}>
        <div>
          <h2>Good Morning, Vikas 👋</h2>
          <p>Friday, 05 Aug 2026 | Book AUM: <strong>₹42.50 Cr</strong> (34 Active Folios / Demat Accounts)</p>
        </div>
        <div className={styles.bannerBadge}>
          <span>3 Action Required Alerts</span>
        </div>
      </div>

      <div className={styles.gridTwoCol}>
        <Card title="Action Required">
          <div className={styles.alertList}>
            <div 
              className={styles.alertItemItem} 
              onClick={() => { setSelectedClient("Aarav Sharma"); setViewMode("drift_detail"); }}
            >
              <div className={`${styles.alertIcon} ${styles.alertIconRed}`} />
              <div className={styles.alertText}>
                <strong>Aarav Sharma</strong>
                <p>Asset Allocation Drift &gt; 15% — equity overweight</p>
              </div>
              <button className={styles.actionPill}>Initiate Portfolio Review</button>
            </div>

            <div className={styles.alertItemItem}>
              <div className={`${styles.alertIcon} ${styles.alertIconAmber}`} />
              <div className={styles.alertText}>
                <strong>Priya Patel</strong>
                <p>₹25.00 Lakh awaiting deployment</p>
              </div>
              <button className={styles.actionPill} onClick={() => {
                setSelectedClient("Priya Patel");
                setInputValue("Help me deploy ₹25.00 Lakh for Priya Patel");
                setViewMode("chat");
              }}>Deploy Capital (Non-Discretionary)</button>
            </div>

            <div className={styles.alertItemItem}>
              <div className={`${styles.alertIcon} ${styles.alertIconAmber}`} />
              <div className={styles.alertText}>
                <strong>Kabir Singh</strong>
                <p>SIP payment pending — auto-retry 07 Aug</p>
              </div>
              <button className={styles.actionPill} onClick={() => {
                setSelectedClient("Kabir Singh");
                setInputValue("How do I resolve the TAT exception for Kabir Singh's SIP?");
                setViewMode("chat");
              }}>Resolve TAT Exception</button>
            </div>
          </div>
        </Card>

        <Card title="Today's Schedule">
          <div className={styles.scheduleList}>
            <div className={styles.scheduleItem}>
              <span className={styles.timeBadge}>10:00 AM</span>
              <span><strong>Aarav Sharma</strong> — Rebalancing & Review</span>
            </div>
            <div className={styles.scheduleItem}>
              <span className={styles.timeBadge}>11:30 AM</span>
              <span><strong>Rohan Mehta</strong> — Quarterly Portfolio Pitch</span>
            </div>
            <div className={styles.scheduleItem}>
              <span className={styles.timeBadge}>03:00 PM</span>
              <span>Investment Committee Briefing</span>
            </div>
          </div>

          <div className={styles.marketBriefing}>
            <div className={styles.marketBriefingLabel}>Market</div>
            <p>NIFTY 50 +0.42% — IT & BFSI leading</p>
            <p>RBI Repo 6.5% — debt yields stable</p>
          </div>
        </Card>
      </div>

      <Card title="Actionable Client Triggers">
        <table className={styles.globalTable}>
          <thead>
            <tr>
              <th>Client Name</th>
              <th>Assets Under Management (AUM)</th>
              <th>Model Portfolio</th>
              <th>Current Allocation</th>
              <th>Max Variance</th>
              <th>Recommended Intervention</th>
            </tr>
          </thead>
          <tbody>
            <tr onClick={() => { setSelectedClient("Aarav Sharma"); setViewMode("drift_detail"); }} style={{ cursor: "pointer" }}>
              <td><strong>Aarav Sharma</strong></td>
              <td>₹1.24 Cr</td>
              <td>50E / 40D / 10C</td>
              <td>65E / 25D / 10C</td>
              <td><StatusPill severity="red">🔴 +15.0% Equity</StatusPill></td>
              <td>
                <Button variant="primary-small">⚡ Rebalance Details</Button>
              </td>
            </tr>
            <tr>
              <td><strong>Priya Patel</strong></td>
              <td>₹4.80 Cr</td>
              <td>70E / 30D</td>
              <td>77E / 23D</td>
              <td><StatusPill severity="amber">🟡 +7.0% Equity</StatusPill></td>
              <td>
                <Button variant="secondary-small">View Options</Button>
              </td>
            </tr>
            <tr>
              <td><strong>Rohan Mehta</strong></td>
              <td>₹2.10 Cr</td>
              <td>30E / 70D</td>
              <td>24E / 76D</td>
              <td><StatusPill severity="amber">🟡 +6.0% Debt</StatusPill></td>
              <td>
                <Button variant="secondary-small">Review Debt</Button>
              </td>
            </tr>
          </tbody>
        </table>
      </Card>
    </div>
  );
}
