from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.websocket.manager import manager
from app.services import match_service

router = APIRouter(tags=["WebSocket"])

@router.websocket("/ws/rooms/{room_code}")
async def websocket_endpoint(websocket: WebSocket, room_code: str, player_name: str, db: Session = Depends(get_db)):
    room_code = room_code.upper()
    await manager.connect(websocket, room_code)
    
    await manager.broadcast_to_room({
        "event": "room_updated",
        "message": f"{player_name} joined the room sync."
    }, room_code)

    try:
        while True:
            data = await websocket.receive_json()
            
            action_type = data.get("type")
            allowed_actions = ["place_reinforcement", "advance_phase", "attack", "move_troops", "end_turn"]
            
            if action_type in allowed_actions:
                try:
                    new_state = match_service.handle_player_action(db, room_code, player_name, data)
                    
                    await manager.broadcast_to_room({
                        "event": "match_state_updated",
                        "state": new_state
                    }, room_code)
                    
                except ValueError as e:
                    await manager.send_personal_message({
                        "event": "action_rejected",
                        "reason": str(e)
                    }, websocket)
            else:
                await manager.send_personal_message({
                    "event": "action_rejected",
                    "reason": "Unknown or forbidden action."
                }, websocket)

    except WebSocketDisconnect:
        manager.disconnect(websocket, room_code)
        await manager.broadcast_to_room({
            "event": "room_updated",
            "message": f"{player_name} disconnected."
        }, room_code)
