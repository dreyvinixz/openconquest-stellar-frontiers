import React from 'react';
import './Card.css';

interface CardProps {
  children: React.ReactNode;
  className?: string;
  glow?: boolean;
  style?: React.CSSProperties;
}

export function Card({ children, className = '', glow = false, style }: CardProps) {
  return (
    <div className={`glass-panel card ${glow ? 'card-glow' : ''} ${className}`} style={style}>
      {children}
    </div>
  );
}
