import { useEffect } from 'react';
import { Lobby } from './pages/Lobby';
import { GalaxyMapPlaceholder } from './pages/GalaxyMapPlaceholder';
import { useGameStore } from './store/useGameStore';
import { connectWebSocket, disconnectWebSocket } from './services/ws';

function App() {
  const { matchState, roomCode, playerName } = useGameStore();

  useEffect(() => {
    if (roomCode && playerName) {
      connectWebSocket(roomCode, playerName);
    }
    return () => {
      disconnectWebSocket();
    };
  }, [roomCode, playerName]);

  return (
    <>
      {!matchState ? <Lobby /> : <GalaxyMapPlaceholder />}
    </>
  );
}

export default App;
