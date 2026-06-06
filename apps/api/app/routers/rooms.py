from fastapi import APIRouter, Header, HTTPException
from typing import Annotated

from app.schemas.room import (
    RoomCreateRequest,
    RoomJoinRequest,
    RoomResponse,
    JoinResponse,
    PlayerResponse,
    StartMatchResponse
)
from app.services.room_service import RoomService

router = APIRouter(prefix="/rooms", tags=["Rooms"])

def _to_response(room) -> RoomResponse:
    return RoomResponse(
        room_code=room.room_code,
        status=room.status,
        max_players=room.max_players,
        map_id=room.map_id,
        players=[PlayerResponse(id=p.id, name=p.name, is_host=p.is_host) for p in room.players]
    )

@router.post("", response_model=JoinResponse, status_code=201)
def create_room(request: RoomCreateRequest):
    room, host = RoomService.create_room(
        host_name=request.player_name,
        max_players=request.max_players,
        map_id=request.map_id
    )
    return JoinResponse(
        room_code=room.room_code,
        player_id=host.id,
        player_token=host.token
    )

@router.get("", response_model=list[RoomResponse])
def list_rooms():
    rooms = RoomService.list_waiting_rooms()
    return [_to_response(r) for r in rooms]

@router.get("/{room_code}", response_model=RoomResponse)
def get_room(room_code: str):
    room = RoomService.get_room(room_code)
    return _to_response(room)

@router.post("/{room_code}/join", response_model=JoinResponse)
def join_room(room_code: str, request: RoomJoinRequest):
    room, player = RoomService.join_room(room_code, request.player_name)
    return JoinResponse(
        room_code=room.room_code,
        player_id=player.id,
        player_token=player.token
    )

@router.post("/{room_code}/start", response_model=StartMatchResponse)
def start_room(room_code: str, authorization: Annotated[str | None, Header()] = None):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    token = authorization.replace("Bearer ", "")
    match_id = RoomService.start_match(room_code, token)
    return StartMatchResponse(match_id=match_id)
