import { create } from 'zustand';

interface GameState {
  playerName: string;
  roomCode: string;
  playerToken: string;
  isConnected: boolean;
  matchState: any | null;
  setPlayerInfo: (name: string, room: string, token?: string) => void;
  setConnectionStatus: (status: boolean) => void;
  setMatchState: (state: any) => void;
  reset: () => void;
}

export const useGameStore = create<GameState>((set) => ({
  playerName: '',
  roomCode: '',
  playerToken: '',
  isConnected: false,
  matchState: null,

  setPlayerInfo: (name, room, token = '') => 
    set((state) => ({ 
      playerName: name, 
      roomCode: room, 
      playerToken: token || state.playerToken 
    })),
    
  setConnectionStatus: (status) => set({ isConnected: status }),
  
  setMatchState: (state) => set({ matchState: state }),
  
  reset: () => set({ 
    playerName: '', 
    roomCode: '', 
    playerToken: '', 
    isConnected: false, 
    matchState: null 
  })
}));
