from fastapi import APIRouter, Header, HTTPException, Depends
from typing import Annotated
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.room import (
    RoomCreateRequest,
    RoomJoinRequest,
    RoomResponse,
    JoinResponse,
    PlayerResponse,
    StartMatchResponse
)
from app.services.room_service import RoomService
from app.models.room import Room

router = APIRouter(prefix="/rooms", tags=["Rooms"])

def _to_response(room: Room) -> RoomResponse:
    return RoomResponse(
        room_code=room.id,
        status=room.status,
        max_players=room.max_players,
        map_id=room.map_id,
        players=[PlayerResponse(id=p.id, name=p.player_name, is_host=p.is_host) for p in room.players]
    )

@router.post("", response_model=JoinResponse, status_code=201)
def create_room(request: RoomCreateRequest, db: Session = Depends(get_db)):
    room, host = RoomService.create_room(
        db=db,
        host_name=request.player_name,
        max_players=request.max_players,
        map_id=request.map_id
    )
    return JoinResponse(
        room_code=room.id,
        player_id=host.id,
        player_token=host.token
    )

@router.get("", response_model=list[RoomResponse])
def list_rooms(db: Session = Depends(get_db)):
    rooms = RoomService.list_waiting_rooms(db)
    return [_to_response(r) for r in rooms]

@router.get("/{room_code}", response_model=RoomResponse)
def get_room(room_code: str, db: Session = Depends(get_db)):
    room = RoomService.get_room(db, room_code.upper())
    return _to_response(room)

@router.post("/{room_code}/join", response_model=JoinResponse)
def join_room(room_code: str, request: RoomJoinRequest, db: Session = Depends(get_db)):
    room, player = RoomService.join_room(db, room_code.upper(), request.player_name)
    return JoinResponse(
        room_code=room.id,
        player_id=player.id,
        player_token=player.token
    )

@router.post("/{room_code}/start", response_model=StartMatchResponse)
def start_room(room_code: str, authorization: Annotated[str | None, Header()] = None, db: Session = Depends(get_db)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    token = authorization.replace("Bearer ", "")
    match_id = RoomService.start_match(db, room_code.upper(), token)
    return StartMatchResponse(match_id=match_id)
