import React from 'react';
import styles from '../app/page.module.css';

interface StatusPillProps {
  severity: 'red' | 'amber' | 'green' | 'blue';
  children: React.ReactNode;
}

export function StatusPill({ severity, children }: StatusPillProps) {
  let pillClass = styles.tagBlue;
  if (severity === 'red') pillClass = styles.tagRed;
  if (severity === 'amber') pillClass = styles.tagAmber;
  if (severity === 'green') pillClass = styles.tagGreen;

  return (
    <span className={pillClass}>
      {children}
    </span>
  );
}
