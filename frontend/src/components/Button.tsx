import React from 'react';
import styles from '../app/page.module.css';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary-small' | 'secondary-small' | 'primary-large' | 'secondary-large';
}

export function Button({ variant = 'primary-small', className, children, ...props }: ButtonProps) {
  let btnClass = styles.btnPrimarySmall;
  if (variant === 'secondary-small') btnClass = styles.btnSecondarySmall;
  if (variant === 'primary-large') btnClass = styles.btnPrimaryLarge;
  if (variant === 'secondary-large') btnClass = styles.btnSecondaryLarge;

  return (
    <button className={`${btnClass} ${className || ''}`} {...props}>
      {children}
    </button>
  );
}
