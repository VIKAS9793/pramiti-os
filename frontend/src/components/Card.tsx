import React from 'react';
import styles from '../app/page.module.css';

interface CardProps {
  title?: string;
  children: React.ReactNode;
  className?: string;
}

export function Card({ title, children, className }: CardProps) {
  return (
    <div className={`${styles.card} glass-panel ${className || ''}`}>
      {title && (
        <div className={styles.cardHeader}>
          <h3>{title}</h3>
        </div>
      )}
      {children}
    </div>
  );
}
