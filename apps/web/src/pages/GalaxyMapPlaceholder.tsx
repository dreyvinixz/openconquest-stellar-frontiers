import { useGameStore } from '../store/useGameStore';
import { Card } from '../components/Card';
import { Button } from '../components/Button';
import { sendAction } from '../services/ws';

export function GalaxyMapPlaceholder() {
  const { matchState, playerName } = useGameStore();

  const isMyTurn = matchState?.players[matchState.current_player_id]?.name === playerName;

  const handleAdvance = () => {
    sendAction('advance_phase');
  };

  const handleEndTurn = () => {
    sendAction('end_turn');
  };

  return (
    <div style={{ padding: '2rem', display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h2 className="text-gradient">Sector: {matchState?.room_code}</h2>
          <p className="text-muted">Round {matchState?.round_number} • {matchState?.phase}</p>
        </div>
        <Card style={{ padding: '1rem' }}>
          <h3 style={{ margin: 0 }}>
            {isMyTurn ? <span className="text-glow" style={{ color: 'var(--success-green)' }}>YOUR TURN</span> : `Waiting for ${matchState?.players[matchState.current_player_id]?.name}...`}
          </h3>
        </Card>
      </header>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 300px', gap: '2rem' }}>
        <Card glow style={{ minHeight: '500px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <div style={{ textAlign: 'center', opacity: 0.5 }}>
            <h1 style={{ fontSize: '4rem', marginBottom: '1rem' }}>🌌</h1>
            <h2>SVG Galaxy Map Loading...</h2>
            <p>Task 6 Placeholder</p>
          </div>
        </Card>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <Card>
            <h3>Command Center</h3>
            {isMyTurn && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', marginTop: '1rem' }}>
                <Button onClick={handleAdvance} variant="secondary">Advance Phase</Button>
                <Button onClick={handleEndTurn} variant="primary">End Turn</Button>
              </div>
            )}
          </Card>

          <Card style={{ flex: 1, overflowY: 'auto' }}>
            <h3>Comms Log</h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', marginTop: '1rem', fontSize: '0.85rem' }}>
              {matchState?.action_log?.slice(-10).map((log: any, i: number) => (
                <div key={i} style={{ padding: '0.5rem', background: 'rgba(0,0,0,0.2)', borderRadius: '4px' }}>
                  <span style={{ color: 'var(--primary-cyan)' }}>[{log.type}]</span> {log.message}
                </div>
              ))}
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}
