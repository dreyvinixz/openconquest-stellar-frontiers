from sqlalchemy.orm import Session
from app.models.match import Match
from app.game_engine.state import MatchState
from app.game_engine.validators import GameActionError

# Pure functions from the engine
from app.game_engine.reducer import (
    place_reinforcement,
    advance_phase,
    attack,
    move_troops,
    end_turn
)

def handle_player_action(db: Session, room_code: str, player_name: str, action_data: dict) -> dict:
    match = db.query(Match).filter(Match.room_id == room_code).first()
    if not match:
        raise ValueError("Match not found")

    # Deserialize pure game state
    current_state = MatchState(**match.state_json)

    # Resolve player_id from player_name
    player_id = next((p.id for p in current_state.players.values() if p.name == player_name), None)
    if not player_id:
        raise ValueError(f"Player '{player_name}' not found in this match")

    action_type = action_data.get("type")
    payload = action_data.get("payload", {})

    try:
        if action_type == "place_reinforcement":
            new_state = place_reinforcement(current_state, player_id, **payload)
        elif action_type == "advance_phase":
            new_state = advance_phase(current_state, player_id)
        elif action_type == "attack":
            new_state = attack(current_state, player_id, **payload)
        elif action_type == "move_troops":
            new_state = move_troops(current_state, player_id, **payload)
        elif action_type == "end_turn":
            new_state = end_turn(current_state, player_id)
        else:
            raise ValueError(f"Unknown or forbidden action type: {action_type}")
    except GameActionError as e:
        # Business logic validation failure from the engine
        raise ValueError(str(e))

    # Persist the new state
    new_state_json = new_state.model_dump(mode="json")
    match.state_json = new_state_json
    db.commit()

    return new_state_json
