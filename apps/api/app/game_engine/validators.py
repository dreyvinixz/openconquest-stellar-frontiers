from __future__ import annotations

from .state import GamePhase, MatchState


class GameActionError(ValueError):
    """Raised when a player submits an invalid game action."""


def validate_current_player(state: MatchState, player_id: str) -> None:
    if state.phase == GamePhase.FINISHED:
        raise GameActionError("Match already finished")
    if player_id != state.current_player_id:
        raise GameActionError("It is not your turn")
    if player_id not in state.players:
        raise GameActionError("Player not found")
    if state.players[player_id].eliminated:
        raise GameActionError("Eliminated players cannot act")


def validate_phase(state: MatchState, expected: GamePhase, action_name: str) -> None:
    if state.phase != expected:
        raise GameActionError(f"{action_name} is not allowed in phase {state.phase.value}")


def validate_reinforcement_action(state: MatchState, player_id: str, territory_id: str, troops: int) -> None:
    validate_current_player(state, player_id)
    validate_phase(state, GamePhase.REINFORCEMENT, "Reinforcement")
    if troops < 1:
        raise GameActionError("You must place at least 1 troop")
    if territory_id not in state.territories:
        raise GameActionError("Territory not found")
    territory = state.territories[territory_id]
    if territory.owner_id != player_id:
        raise GameActionError("This territory does not belong to you")
    pool = state.players[player_id].reinforcement_pool
    if troops > pool:
        raise GameActionError(f"You only have {pool} reinforcement troops")


def validate_attack_action(state: MatchState, player_id: str, source_id: str, target_id: str, attacking_troops: int) -> None:
    validate_current_player(state, player_id)
    validate_phase(state, GamePhase.ATTACK, "Attack")
    if attacking_troops < 1:
        raise GameActionError("Attack must use at least 1 troop")
    if source_id not in state.territories or target_id not in state.territories:
        raise GameActionError("Territory not found")
    source = state.territories[source_id]
    target = state.territories[target_id]
    if source.owner_id != player_id:
        raise GameActionError("Source territory does not belong to you")
    if target.owner_id == player_id:
        raise GameActionError("Cannot attack your own territory")
    if target.owner_id is None:
        raise GameActionError("Cannot attack a neutral territory in MVP")
    if target_id not in source.neighbors:
        raise GameActionError("Target territory is not adjacent")
    if source.troops < 2:
        raise GameActionError("Source territory must have at least 2 troops")
    if attacking_troops >= source.troops:
        raise GameActionError("You must leave at least 1 behind")


def validate_movement_action(state: MatchState, player_id: str, source_id: str, target_id: str, troops: int) -> None:
    validate_current_player(state, player_id)
    validate_phase(state, GamePhase.MOVEMENT, "Movement")
    if troops < 1:
        raise GameActionError("Movement must use at least 1 troop")
    if source_id not in state.territories or target_id not in state.territories:
        raise GameActionError("Territory not found")
    source = state.territories[source_id]
    target = state.territories[target_id]
    if source.owner_id != player_id:
        raise GameActionError("Source territory does not belong to you")
    if target.owner_id != player_id:
        raise GameActionError("Target territory does not belong to you")
    if source.troops < 2:
        raise GameActionError("Source territory must have at least 2 troops")
    if troops >= source.troops:
        raise GameActionError("You must leave at least 1 troop behind")
    if target_id not in source.neighbors:
        raise GameActionError("Target territory is not adjacent")
    if state.movement_used_this_turn:
        raise GameActionError("Movement already used this turn")


def validate_end_turn_action(state: MatchState, player_id: str) -> None:
    validate_current_player(state, player_id)
    if state.phase not in {GamePhase.ATTACK, GamePhase.MOVEMENT}:
        raise GameActionError("End turn is not allowed before attack or movement phase")
