const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export async function createRoom(playerName: string, maxPlayers: number = 2) {
  const res = await fetch(`${API_URL}/rooms`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ player_name: playerName, max_players: maxPlayers })
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function joinRoom(roomCode: string, playerName: string) {
  const res = await fetch(`${API_URL}/rooms/${roomCode}/join`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ player_name: playerName })
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function startMatch(roomCode: string, token: string) {
  const res = await fetch(`${API_URL}/rooms/${roomCode}/start`, {
    method: 'POST',
    headers: { 
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    }
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}
