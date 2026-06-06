from dataclasses import dataclass, field
from typing import Optional
from uuid import uuid4

@dataclass
class RoomPlayerModel:
    id: str
    name: str
    is_host: bool
    token: str = field(default_factory=lambda: str(uuid4()))

@dataclass
class RoomModel:
    room_code: str
    max_players: int
    map_id: str
    status: str = "waiting" # waiting, started
    match_id: Optional[str] = None
    players: list[RoomPlayerModel] = field(default_factory=list)

    @property
    def host_id(self) -> str:
        for p in self.players:
            if p.is_host:
                return p.id
        raise ValueError("Room has no host")
