"""
Tests: Reinforcement, phase advance, and troop movement.
"""

from __future__ import annotations

import pytest

from app.game_engine.reducer import advance_phase, move_troops, place_reinforcement
from app.game_engine.state import GamePhase
from app.game_engine.validators import GameActionError
from tests.conftest import make_match


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def get_current_player_id(state):
    return state.current_player_id


def get_current_player(state):
    return state.players[state.current_player_id]


def get_owned_territory(state, player_id):
    """Return first territory owned by the player."""
    for t in state.territories.values():
        if t.owner_id == player_id:
            return t
    raise ValueError(f"No territory owned by {player_id}")


def get_enemy_territory(state, player_id):
    """Return first territory NOT owned by the player."""
    for t in state.territories.values():
        if t.owner_id is not None and t.owner_id != player_id:
            return t
    raise ValueError("No enemy territory found")


def drain_reinforcement_pool(state):
    """Place all remaining reinforcement troops on the first owned territory."""
    pid = state.current_player_id
    pool = state.players[pid].reinforcement_pool
    if pool > 0:
        territory = get_owned_territory(state, pid)
        state = place_reinforcement(state, pid, territory.id, pool)
    return state


# ---------------------------------------------------------------------------
# Reinforcement
# ---------------------------------------------------------------------------


class TestPlaceReinforcement:
    def test_places_troops_on_owned_territory(self):
        state = make_match()
        pid = get_current_player_id(state)
        territory = get_owned_territory(state, pid)
        troops_before = territory.troops
        pool = state.players[pid].reinforcement_pool

        new_state = place_reinforcement(state, pid, territory.id, 1)

        assert new_state.territories[territory.id].troops == troops_before + 1
        assert new_state.players[pid].reinforcement_pool == pool - 1

    def test_drains_full_pool(self):
        state = make_match()
        pid = get_current_player_id(state)
        pool = state.players[pid].reinforcement_pool
        territory = get_owned_territory(state, pid)

        new_state = place_reinforcement(state, pid, territory.id, pool)
        assert new_state.players[pid].reinforcement_pool == 0

    def test_rejects_placing_on_enemy_territory(self):
        state = make_match()
        pid = get_current_player_id(state)
        enemy_territory = get_enemy_territory(state, pid)

        with pytest.raises(GameActionError, match="does not belong to you"):
            place_reinforcement(state, pid, enemy_territory.id, 1)

    def test_rejects_zero_troops(self):
        state = make_match()
        pid = get_current_player_id(state)
        territory = get_owned_territory(state, pid)

        with pytest.raises(GameActionError, match="at least 1"):
            place_reinforcement(state, pid, territory.id, 0)

    def test_rejects_negative_troops(self):
        state = make_match()
        pid = get_current_player_id(state)
        territory = get_owned_territory(state, pid)

        with pytest.raises(GameActionError, match="at least 1"):
            place_reinforcement(state, pid, territory.id, -1)

    def test_rejects_exceeding_pool(self):
        state = make_match()
        pid = get_current_player_id(state)
        territory = get_owned_territory(state, pid)
        pool = state.players[pid].reinforcement_pool

        with pytest.raises(GameActionError, match="only have"):
            place_reinforcement(state, pid, territory.id, pool + 99)

    def test_rejects_non_current_player(self):
        state = make_match()
        pid = get_current_player_id(state)
        other_pid = [p for p in state.player_order if p != pid][0]
        territory = get_owned_territory(state, other_pid)

        with pytest.raises(GameActionError, match="not your turn"):
            place_reinforcement(state, other_pid, territory.id, 1)

    def test_rejects_in_wrong_phase(self):
        state = make_match()
        pid = get_current_player_id(state)
        # Drain pool and advance to attack phase
        state = drain_reinforcement_pool(state)
        state = advance_phase(state, pid)
        assert state.phase == GamePhase.ATTACK

        territory = get_owned_territory(state, pid)
        with pytest.raises(GameActionError, match="not allowed"):
            place_reinforcement(state, pid, territory.id, 1)

    def test_logs_reinforcement_action(self):
        state = make_match()
        pid = get_current_player_id(state)
        territory = get_owned_territory(state, pid)

        new_state = place_reinforcement(state, pid, territory.id, 1)
        types = [e.type for e in new_state.action_log]
        assert "reinforcement" in types

    def test_can_place_in_multiple_territories(self):
        state = make_match()
        pid = get_current_player_id(state)
        owned = [t for t in state.territories.values() if t.owner_id == pid]
        assert len(owned) >= 2, "Need at least 2 owned territories for this test"

        state = place_reinforcement(state, pid, owned[0].id, 1)
        state = place_reinforcement(state, pid, owned[1].id, 1)
        assert state.territories[owned[0].id].troops == 2
        assert state.territories[owned[1].id].troops == 2


# ---------------------------------------------------------------------------
# Phase advance
# ---------------------------------------------------------------------------


class TestAdvancePhase:
    def test_advances_from_reinforcement_to_attack(self):
        state = make_match()
        pid = get_current_player_id(state)
        state = drain_reinforcement_pool(state)

        new_state = advance_phase(state, pid)
        assert new_state.phase == GamePhase.ATTACK

    def test_advances_from_attack_to_movement(self):
        state = make_match()
        pid = get_current_player_id(state)
        state = drain_reinforcement_pool(state)
        state = advance_phase(state, pid)
        assert state.phase == GamePhase.ATTACK

        new_state = advance_phase(state, pid)
        assert new_state.phase == GamePhase.MOVEMENT

    def test_rejects_advance_with_remaining_pool(self):
        state = make_match()
        pid = get_current_player_id(state)
        # Pool is > 0, should not be able to advance
        assert state.players[pid].reinforcement_pool > 0
        with pytest.raises(GameActionError, match="must place all"):
            advance_phase(state, pid)

    def test_rejects_non_current_player(self):
        state = make_match()
        pid = get_current_player_id(state)
        state = drain_reinforcement_pool(state)
        other_pid = [p for p in state.player_order if p != pid][0]

        with pytest.raises(GameActionError, match="not your turn"):
            advance_phase(state, other_pid)

    def test_logs_phase_change(self):
        state = make_match()
        pid = get_current_player_id(state)
        state = drain_reinforcement_pool(state)

        new_state = advance_phase(state, pid)
        types = [e.type for e in new_state.action_log]
        assert "phase_changed" in types


# ---------------------------------------------------------------------------
# Movement
# ---------------------------------------------------------------------------


class TestMoveTroops:
    def _get_to_movement_phase(self, state):
        """Advance state to movement phase for the current player."""
        pid = state.current_player_id
        state = drain_reinforcement_pool(state)
        state = advance_phase(state, pid)  # → attack
        state = advance_phase(state, pid)  # → movement
        return state

    def test_moves_troops_between_adjacent_owned_territories(self):
        state = make_match()
        pid = get_current_player_id(state)
        state = self._get_to_movement_phase(state)

        # Find two adjacent owned territories
        source = None
        target_id = None
        for t in state.territories.values():
            if t.owner_id == pid and t.troops >= 2:
                for neighbor_id in t.neighbors:
                    neighbor = state.territories[neighbor_id]
                    if neighbor.owner_id == pid:
                        source = t
                        target_id = neighbor_id
                        break
            if source:
                break

        if source is None or target_id is None:
            pytest.skip("No adjacent owned territories available in this map distribution")

        troops_before_source = source.troops
        troops_before_target = state.territories[target_id].troops

        new_state = move_troops(state, pid, source.id, target_id, 1)

        assert new_state.territories[source.id].troops == troops_before_source - 1
        assert new_state.territories[target_id].troops == troops_before_target + 1

    def test_rejects_moving_to_enemy_territory(self):
        state = make_match()
        pid = get_current_player_id(state)
        state = self._get_to_movement_phase(state)

        # Find owned territory with an enemy neighbor
        source = None
        enemy_id = None
        for t in state.territories.values():
            if t.owner_id == pid and t.troops >= 2:
                for nid in t.neighbors:
                    if state.territories[nid].owner_id != pid:
                        source = t
                        enemy_id = nid
                        break
            if source:
                break

        if source is None:
            pytest.skip("No owned territory with an enemy neighbor found")

        with pytest.raises(GameActionError, match="does not belong to you"):
            move_troops(state, pid, source.id, enemy_id, 1)

    def test_rejects_moving_from_enemy_territory(self):
        state = make_match()
        pid = get_current_player_id(state)
        state = self._get_to_movement_phase(state)

        enemy_territory = get_enemy_territory(state, pid)
        owned_territory = get_owned_territory(state, pid)

        with pytest.raises(GameActionError, match="does not belong to you"):
            move_troops(state, pid, enemy_territory.id, owned_territory.id, 1)

    def test_rejects_moving_all_troops(self):
        state = make_match()
        pid = get_current_player_id(state)
        state = self._get_to_movement_phase(state)

        # First reinforce a territory to have 2+ troops
        source = get_owned_territory(state, pid)

        with pytest.raises(GameActionError, match="must leave at least 1"):
            move_troops(state, pid, source.id, source.id, source.troops)

    def test_rejects_non_adjacent_movement(self):
        state = make_match()
        pid = get_current_player_id(state)
        state = self._get_to_movement_phase(state)

        # Find two owned territories that are NOT adjacent
        owned = [t for t in state.territories.values() if t.owner_id == pid]
        source = None
        non_adjacent_id = None
        for t in owned:
            for other in owned:
                if other.id not in t.neighbors and other.id != t.id and t.troops >= 2:
                    source = t
                    non_adjacent_id = other.id
                    break
            if source:
                break

        if source is None:
            pytest.skip("No non-adjacent owned territory pair in this distribution")

        with pytest.raises(GameActionError, match="not adjacent"):
            move_troops(state, pid, source.id, non_adjacent_id, 1)

    def test_rejects_movement_in_wrong_phase(self):
        state = make_match()
        pid = get_current_player_id(state)
        # Still in reinforcement phase
        source = get_owned_territory(state, pid)

        with pytest.raises(GameActionError, match="not allowed"):
            move_troops(state, pid, source.id, source.id, 1)

    def test_logs_movement(self):
        state = make_match()
        pid = get_current_player_id(state)
        state = self._get_to_movement_phase(state)

        # Find two adjacent owned territories
        source = None
        target_id = None
        for t in state.territories.values():
            if t.owner_id == pid and t.troops >= 2:
                for nid in t.neighbors:
                    if state.territories[nid].owner_id == pid:
                        source = t
                        target_id = nid
                        break
            if source:
                break

        if source is None:
            pytest.skip("No adjacent owned territory pair")

        new_state = move_troops(state, pid, source.id, target_id, 1)
        types = [e.type for e in new_state.action_log]
        assert "troop_movement" in types
