from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class EngineModel(BaseModel):
    """Pydantic model with a compatibility helper used by the tests."""

    def model_copy_update(self, **updates):
        return self.model_copy(update=updates)


class GamePhase(str, Enum):
    LOBBY = "lobby"
    REINFORCEMENT = "reinforcement"
    ATTACK = "attack"
    MOVEMENT = "movement"
    FINISHED = "finished"


class ObjectiveType(str, Enum):
    CONTROL_TERRITORY_COUNT = "control_territory_count"
    CONTROL_REGION_COUNT = "control_region_count"
    CONTROL_SPECIFIC_REGIONS = "control_specific_regions"
    ELIMINATE_PLAYER_COUNT = "eliminate_player_count"


class Player(EngineModel):
    id: str
    name: str
    color: str
    objective_id: str | None = None
    is_host: bool = False
    is_connected: bool = True
    eliminated: bool = False
    reinforcement_pool: int = 0
    territories_conquered_this_turn: int = 0
    players_eliminated: int = 0


class Territory(EngineModel):
    """Generic node in the engine. In the space theme this is a planet/station."""

    id: str
    name: str
    region: str
    terrain: str
    owner_id: str | None = None
    troops: int = 0  # Theme label: fleets
    neighbors: list[str] = Field(default_factory=list)
    x: float = 0
    y: float = 0


class Region(EngineModel):
    """Generic region in the engine. In the space theme this is a galactic sector."""

    id: str
    name: str
    bonus_troops: int
    territory_ids: list[str]


class Objective(EngineModel):
    id: str
    title: str
    description: str
    type: ObjectiveType | str
    params: dict[str, Any] = Field(default_factory=dict)


class GameLogEntry(EngineModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    type: str
    player_id: str
    message: str
    payload: dict[str, Any] = Field(default_factory=dict)


class MatchState(EngineModel):
    match_id: str
    room_code: str
    status: str = "started"
    round_number: int = 1
    current_player_id: str
    phase: GamePhase = GamePhase.REINFORCEMENT
    players: dict[str, Player]
    player_order: list[str]
    territories: dict[str, Territory]
    regions: dict[str, Region]
    objectives: dict[str, Objective]
    action_log: list[GameLogEntry] = Field(default_factory=list)
    winner_player_id: str | None = None
    movement_used_this_turn: bool = False
