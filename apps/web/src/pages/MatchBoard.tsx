import { useState } from 'react';
import { useGameStore } from '../store/useGameStore';
import { Card } from '../components/Card';
import { Button } from '../components/Button';
import { GalaxyMap } from '../components/GalaxyMap';
import { ActionModal } from '../components/ActionModal';
import { sendAction } from '../services/ws';

export function MatchBoard() {
  const { matchState, playerName } = useGameStore();
  const [selectedNode, setSelectedNode] = useState<string | null>(null);
  const [modalOpen, setModalOpen] = useState(false);
  const [actionType, setActionType] = useState<'reinforce' | 'attack' | 'move' | null>(null);
  const [targetNode, setTargetNode] = useState<string | null>(null);

  if (!matchState) return null;

  const currentPlayerId = matchState.current_player_id;
  const isMyTurn = matchState.players[currentPlayerId]?.name === playerName;
  const myPlayerId = Object.keys(matchState.players).find(id => matchState.players[id].name === playerName);

  console.log('MatchBoard render. round:', matchState.round_number, 'territories exists:', !!matchState.territories);

  const handleNodeClick = (nodeId: string) => {
    if (!isMyTurn) return;

    const territory = matchState.territories[nodeId];
    const isMine = territory.owner_id === myPlayerId;

    if (matchState.phase === 'reinforcement') {
      if (isMine) {
        setSelectedNode(nodeId);
        setActionType('reinforce');
        setModalOpen(true);
      }
      return;
    }

    if (matchState.phase === 'attack' || matchState.phase === 'movement') {
      if (!selectedNode) {
        // Select source
        if (isMine && territory.troops > 1) {
          setSelectedNode(nodeId);
        }
      } else {
        // Select target
        if (nodeId === selectedNode) {
          setSelectedNode(null); // Deselect
          return;
        }
        
        // Check adjacency
        const neighbors = matchState.territories[selectedNode].neighbors || [];
        if (neighbors.includes(nodeId)) {
          setTargetNode(nodeId);
          setActionType(matchState.phase === 'attack' ? 'attack' : 'move');
          setModalOpen(true);
        } else {
          // If clicked another valid source, change selection
          if (isMine && territory.troops > 1) {
            setSelectedNode(nodeId);
          }
        }
      }
    }
  };

  const handleConfirmAction = (troops: number) => {
    if (actionType === 'reinforce' && selectedNode) {
      sendAction('place_reinforcement', { territory_id: selectedNode, troops });
    } else if (actionType === 'attack' && selectedNode && targetNode) {
      sendAction('attack', { source_id: selectedNode, target_id: targetNode, attacking_troops: troops });
    } else if (actionType === 'move' && selectedNode && targetNode) {
      sendAction('move_troops', { source_id: selectedNode, target_id: targetNode, moving_troops: troops });
    }
    
    // Reset selection after action attempt (backend will broadcast result)
    setModalOpen(false);
    setSelectedNode(null);
    setTargetNode(null);
    setActionType(null);
  };

  const handleCancelAction = () => {
    setModalOpen(false);
    if (actionType === 'reinforce') setSelectedNode(null);
    setTargetNode(null);
    setActionType(null);
  };

  // Determine max troops for modal
  let maxTroops = 0;
  let modalTitle = '';
  let modalDesc = '';

  if (actionType === 'reinforce') {
    maxTroops = matchState.players[myPlayerId!].reinforcement_pool;
    modalTitle = 'Deploy Fleet';
    modalDesc = `Deploying to ${selectedNode}`;
  } else if ((actionType === 'attack' || actionType === 'move') && selectedNode) {
    maxTroops = matchState.territories[selectedNode].troops - 1; // leave 1 behind
    modalTitle = actionType === 'attack' ? 'Initiate Attack' : 'Move Fleet';
    modalDesc = `From ${selectedNode} to ${targetNode}`;
  }

  const handleAdvance = () => {
    sendAction('advance_phase');
    setSelectedNode(null);
  };

  const handleEndTurn = () => {
    sendAction('end_turn');
    setSelectedNode(null);
  };

  return (
    <div style={{ padding: '2rem', display: 'flex', flexDirection: 'column', gap: '1rem', height: '100vh', boxSizing: 'border-box' }}>
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h2 className="text-gradient">Sector: {matchState.room_code}</h2>
          <p className="text-muted">Round {matchState.round_number} • {matchState.phase}</p>
        </div>
        <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
          <div style={{ textAlign: 'right' }}>
             <p className="text-muted" style={{ margin: 0, fontSize: '0.85rem' }}>Reinforcements</p>
             <h3 style={{ margin: 0, color: 'var(--primary-cyan)' }}>{matchState.players[myPlayerId!]?.reinforcement_pool || 0}</h3>
          </div>
          <Card style={{ padding: '0.5rem 1rem' }}>
            <h3 style={{ margin: 0 }}>
              {isMyTurn ? <span className="text-glow" style={{ color: 'var(--success-green)' }}>YOUR TURN</span> : `Waiting for ${matchState.players[currentPlayerId]?.name}...`}
            </h3>
          </Card>
        </div>
      </header>

      <div style={{ display: 'flex', gap: '2rem', flex: 1, minHeight: 0 }}>
        {/* Main Map Area */}
        <Card glow style={{ flex: 3, padding: 0, position: 'relative', overflow: 'hidden' }}>
          <GalaxyMap 
            matchState={matchState} 
            selectedNode={selectedNode} 
            targetNode={targetNode}
            onNodeClick={handleNodeClick}
          />
          
          {/* Floating Phase Controls */}
          {isMyTurn && (
            <div style={{ position: 'absolute', bottom: '2rem', right: '2rem', display: 'flex', gap: '1rem' }}>
               <Button onClick={handleAdvance} variant="secondary">Advance Phase</Button>
               <Button onClick={handleEndTurn} variant="primary">End Turn</Button>
            </div>
          )}
        </Card>

        {/* Sidebar */}
        <Card style={{ flex: 1, display: 'flex', flexDirection: 'column', padding: '1rem', overflowY: 'auto' }}>
          <h3 style={{ marginBottom: '1rem' }}>Comms Log</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', fontSize: '0.85rem' }}>
            {[...matchState.action_log].reverse().slice(0, 20).map((log: any, i: number) => (
              <div key={i} style={{ padding: '0.5rem', background: 'rgba(0,0,0,0.3)', borderRadius: '4px', borderLeft: '2px solid var(--primary-cyan)' }}>
                <strong style={{ color: 'var(--text-muted)' }}>[{log.type}]</strong><br/>
                {log.message}
              </div>
            ))}
          </div>
        </Card>
      </div>

      {modalOpen && (
        <ActionModal 
          title={modalTitle}
          description={modalDesc}
          maxTroops={maxTroops}
          onConfirm={handleConfirmAction}
          onCancel={handleCancelAction}
        />
      )}
    </div>
  );
}
