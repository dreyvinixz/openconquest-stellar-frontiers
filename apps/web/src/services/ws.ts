import { useGameStore } from '../store/useGameStore';

const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws';
let socket: WebSocket | null = null;

export function connectWebSocket(roomCode: string, playerName: string) {
  if (socket) {
    socket.close();
  }

  socket = new WebSocket(`${WS_URL}/rooms/${roomCode}?player_name=${encodeURIComponent(playerName)}`);

  socket.onopen = () => {
    console.log('Connected to space comms');
    useGameStore.getState().setConnectionStatus(true);
  };

  socket.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      console.log('Intercepted transmission:', data);
      
      if (data.event === 'match_state_updated' && data.state) {
        useGameStore.getState().setMatchState(data.state);
      } else if (data.event === 'action_rejected') {
        alert(`Action Rejected: ${data.reason}`);
      }
    } catch (e) {
      console.error('Failed to parse transmission', e);
    }
  };

  socket.onclose = () => {
    console.log('Comms link lost');
    useGameStore.getState().setConnectionStatus(false);
  };
}

export function sendAction(type: string, payload: any = {}) {
  if (socket && socket.readyState === WebSocket.OPEN) {
    socket.send(JSON.stringify({ type, payload }));
  } else {
    console.warn('Comms link is offline. Cannot send action.');
  }
}

export function disconnectWebSocket() {
  if (socket) {
    socket.close();
    socket = null;
  }
}
