import { useState } from 'react';
import { Card } from '../components/Card';
import { Button } from '../components/Button';
import { Input } from '../components/Input';
import { createRoom, joinRoom, startMatch } from '../services/api';
import { useGameStore } from '../store/useGameStore';
import { Rocket, Users, Play } from 'lucide-react';
import './Lobby.css';

export function Lobby() {
  const [name, setName] = useState('');
  const [roomToJoin, setRoomToJoin] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  const { setPlayerInfo, roomCode, playerToken, isConnected } = useGameStore();

  const handleCreateRoom = async () => {
    if (!name) return setError('Please enter a Commander Name');
    setLoading(true);
    setError('');
    try {
      const data = await createRoom(name);
      setPlayerInfo(name, data.room_code, data.player_token);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const handleJoinRoom = async () => {
    if (!name || !roomToJoin) return setError('Name and Room Code required');
    setLoading(true);
    setError('');
    try {
      await joinRoom(roomToJoin, name);
      setPlayerInfo(name, roomToJoin.toUpperCase());
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const handleStartMatch = async () => {
    setLoading(true);
    setError('');
    try {
      await startMatch(roomCode, playerToken);
      // Wait for WS broadcast to change match state
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  if (roomCode) {
    return (
      <div className="lobby-container">
        <Card glow className="lobby-card">
          <div className="lobby-header">
            <h1 className="text-gradient">Sector {roomCode}</h1>
            <p className="text-muted">Awaiting hyperdrive sequence...</p>
          </div>
          
          <div className="lobby-info">
            <p>Commander: <strong>{name}</strong></p>
            <p>Comms Link: {isConnected ? <span className="status-online">Online</span> : <span className="status-offline">Offline</span>}</p>
          </div>

          {error && <div className="error-banner">{error}</div>}

          {playerToken ? (
            <Button onClick={handleStartMatch} isLoading={loading} className="w-full">
              <Play size={18} /> Initiate Jump
            </Button>
          ) : (
            <p className="text-muted text-center italic">Waiting for Host to start...</p>
          )}
        </Card>
      </div>
    );
  }

  return (
    <div className="lobby-container">
      <div className="brand-header">
        <Rocket size={48} className="brand-icon" />
        <h1 className="text-glow">STELLAR FRONTIERS</h1>
      </div>

      <Card glow className="lobby-card">
        <Input 
          label="Commander Name" 
          placeholder="Enter your alias" 
          value={name} 
          onChange={(e) => setName(e.target.value)} 
          maxLength={15}
        />

        {error && <div className="error-banner">{error}</div>}

        <div className="lobby-actions">
          <Button onClick={handleCreateRoom} isLoading={loading} className="w-full">
            <Rocket size={18} /> Form New Fleet
          </Button>
          
          <div className="divider">
            <span>OR INFILTRATE</span>
          </div>

          <div className="join-row">
            <Input 
              placeholder="Room Code" 
              value={roomToJoin} 
              onChange={(e) => setRoomToJoin(e.target.value.toUpperCase())}
              maxLength={6}
            />
            <Button onClick={handleJoinRoom} variant="secondary" isLoading={loading}>
              <Users size={18} /> Join
            </Button>
          </div>
        </div>
      </Card>
    </div>
  );
}
