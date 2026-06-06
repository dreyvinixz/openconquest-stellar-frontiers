import string
import random
from uuid import uuid4
from fastapi import HTTPException

from app.models.room import RoomModel, RoomPlayerModel
from app.game_engine.reducer import start_match
from app.game_engine.state import MatchState

# In-memory database for MVP
_rooms_db: dict[str, RoomModel] = {}
_matches_db: dict[str, MatchState] = {}

def _generate_room_code() -> str:
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

class RoomService:
    
    @classmethod
    def create_room(cls, host_name: str, max_players: int, map_id: str) -> tuple[RoomModel, RoomPlayerModel]:
        room_code = _generate_room_code()
        while room_code in _rooms_db:
            room_code = _generate_room_code()
            
        host_player = RoomPlayerModel(
            id=str(uuid4()),
            name=host_name,
            is_host=True
        )
        
        room = RoomModel(
            room_code=room_code,
            max_players=max_players,
            map_id=map_id,
            players=[host_player]
        )
        _rooms_db[room_code] = room
        return room, host_player

    @classmethod
    def list_waiting_rooms(cls) -> list[RoomModel]:
        return [r for r in _rooms_db.values() if r.status == "waiting"]

    @classmethod
    def get_room(cls, room_code: str) -> RoomModel:
        room = _rooms_db.get(room_code)
        if not room:
            raise HTTPException(status_code=404, detail="Room not found")
        return room

    @classmethod
    def join_room(cls, room_code: str, player_name: str) -> tuple[RoomModel, RoomPlayerModel]:
        room = cls.get_room(room_code)
        
        if room.status != "waiting":
            raise HTTPException(status_code=400, detail="Room has already started")
            
        if len(room.players) >= room.max_players:
            raise HTTPException(status_code=400, detail="Room is full")
            
        # Optional: Prevent duplicate names
        if any(p.name == player_name for p in room.players):
            raise HTTPException(status_code=400, detail="Name already taken in this room")
            
        new_player = RoomPlayerModel(
            id=str(uuid4()),
            name=player_name,
            is_host=False
        )
        room.players.append(new_player)
        return room, new_player

    @classmethod
    def start_match(cls, room_code: str, player_token: str) -> str:
        room = cls.get_room(room_code)
        
        if room.status != "waiting":
            raise HTTPException(status_code=400, detail="Room is not in waiting state")
            
        if len(room.players) < 2:
            raise HTTPException(status_code=400, detail="Need at least 2 players to start")
            
        # Authorize host
        host = next((p for p in room.players if p.is_host), None)
        if not host or host.token != player_token:
            raise HTTPException(status_code=403, detail="Only the host can start the match")
            
        # Start game via engine
        player_names = [p.name for p in room.players]
        match_state = start_match(player_names=player_names, room_code=room.room_code)
        
        # In a real DB, we would save this to the matches table
        _matches_db[match_state.match_id] = match_state
        
        room.status = "started"
        room.match_id = match_state.match_id
        return match_state.match_id
