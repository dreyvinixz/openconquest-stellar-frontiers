import { useState } from 'react';
import { Card } from './Card';
import { Button } from './Button';
import { Input } from './Input';
import './ActionModal.css';

interface ActionModalProps {
  title: string;
  description: string;
  maxTroops: number;
  onConfirm: (troops: number) => void;
  onCancel: () => void;
}

export function ActionModal({ title, description, maxTroops, onConfirm, onCancel }: ActionModalProps) {
  const [troops, setTroops] = useState(maxTroops);

  return (
    <div className="modal-overlay">
      <Card glow className="modal-content">
        <h2>{title}</h2>
        <p className="text-muted">{description}</p>
        
        <Input 
          type="number" 
          label="Number of Fleets" 
          value={troops} 
          min={1} 
          max={maxTroops}
          onChange={(e) => setTroops(Number(e.target.value))}
        />
        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
          <span>Min: 1</span>
          <span>Max: {maxTroops}</span>
        </div>

        <div className="modal-actions">
          <Button variant="secondary" onClick={onCancel}>Cancel</Button>
          <Button variant="primary" onClick={() => onConfirm(troops)}>Execute</Button>
        </div>
      </Card>
    </div>
  );
}
