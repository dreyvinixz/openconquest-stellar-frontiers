"""
Tests: Attack system.
"""

from __future__ import annotations


import pytest

from app.game_engine.reducer import (
    advance_phase,
    attack,
    place_reinforcement,
)
from app.game_engine.state import GamePhase
from app.game_engine.validators import GameActionError
from tests.conftest import make_match


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def get_to_attack_phase(state):
    """Drain reinforcement pool and advance to attack phase."""
    pid = state.current_player_id
    pool = state.players[pid].reinforcement_pool
    if pool > 0:
        territory = next(
            t for t in state.territories.values() if t.owner_id == pid
        )
        state = place_reinforcement(state, pid, territory.id, pool)
    state = advance_phase(state, pid)
    assert state.phase == GamePhase.ATTACK
    return state


def find_attack_pair(state):
    """
    Find a (source, target) pair where:
    - source belongs to current player and has ≥ 2 troops
    - target belongs to an enemy and is adjacent to source
    Returns (source_territory, target_territory) or (None, None).
    """
    pid = state.current_player_id
    for source in state.territories.values():
        if source.owner_id == pid and source.troops >= 2:
            for nid in source.neighbors:
                target = state.territories[nid]
                if target.owner_id is not None and target.owner_id != pid:
                    return source, target
    return None, None


def reinforce_territory(state, territory_id, troops):
    """Force-add troops to a territory without going through the normal flow (test setup helper)."""
    t = state.territories[territory_id]
    state.territories[territory_id] = t.model_copy_update(troops=t.troops + troops)
    return state


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestAttack:
    def test_attack_requires_attack_phase(self):
        state = make_match()
        pid = state.current_player_id
        source, target = find_attack_pair(make_match())
        if source is None:
            pytest.skip("No attackable pair found")

        # Still in reinforcement phase
        with pytest.raises(GameActionError, match="not allowed"):
            attack(state, pid, source.id, target.id, 1)

    def test_attack_requires_current_player(self):
        state = make_match()
        state = get_to_attack_phase(state)
        pid = state.current_player_id
        other_pid = [p for p in state.player_order if p != pid][0]
        source, target = find_attack_pair(state)
        if source is None:
            pytest.skip("No attackable pair found")

        with pytest.raises(GameActionError, match="not your turn"):
            attack(state, other_pid, source.id, target.id, 1)

    def test_attack_source_must_belong_to_player(self):
        state = make_match()
        state = get_to_attack_phase(state)
        pid = state.current_player_id
        enemy_source = next(
            t for t in state.territories.values()
            if t.owner_id != pid and t.troops >= 2
        )
        owned_target = next(
            t for t in state.territories.values() if t.owner_id == pid
        )

        with pytest.raises(GameActionError, match="does not belong to you"):
            attack(state, pid, enemy_source.id, owned_target.id, 1)

    def test_cannot_attack_own_territory(self):
        state = make_match()
        state = get_to_attack_phase(state)
        pid = state.current_player_id
        owned = [t for t in state.territories.values() if t.owner_id == pid]
        if len(owned) < 2:
            pytest.skip("Need at least 2 owned territories")

        with pytest.raises(GameActionError, match="own territory"):
            attack(state, pid, owned[0].id, owned[1].id, 1)

    def test_cannot_attack_non_adjacent_territory(self):
        state = make_match()
        state = get_to_attack_phase(state)
        pid = state.current_player_id

        # Find owned territory and a non-adjacent enemy
        source = next(
            t for t in state.territories.values()
            if t.owner_id == pid and t.troops >= 2
        )
        non_adjacent_enemy = next(
            (t for t in state.territories.values()
             if t.owner_id != pid and t.id not in source.neighbors),
            None,
        )

        if non_adjacent_enemy is None:
            pytest.skip("No non-adjacent enemy found")

        with pytest.raises(GameActionError, match="not adjacent"):
            attack(state, pid, source.id, non_adjacent_enemy.id, 1)

    def test_cannot_attack_with_all_troops(self):
        state = make_match()
        state = get_to_attack_phase(state)
        pid = state.current_player_id
        source, target = find_attack_pair(state)
        if source is None:
            pytest.skip("No attackable pair")

        with pytest.raises(GameActionError, match="at least 1 behind"):
            attack(state, pid, source.id, target.id, source.troops)

    def test_cannot_attack_with_zero_troops(self):
        state = make_match()
        state = get_to_attack_phase(state)
        pid = state.current_player_id
        source, target = find_attack_pair(state)
        if source is None:
            pytest.skip("No attackable pair")

        with pytest.raises(GameActionError, match="at least 1 troop"):
            attack(state, pid, source.id, target.id, 0)

    def test_source_must_have_at_least_2_troops(self):
        state = make_match()
        state = get_to_attack_phase(state)
        pid = state.current_player_id

        # Find a source with only 1 troop
        one_troop_source = next(
            (t for t in state.territories.values()
             if t.owner_id == pid and t.troops == 1),
            None,
        )
        if one_troop_source is None:
            pytest.skip("No 1-troop source available")

        enemy_neighbor = next(
            (state.territories[nid] for nid in one_troop_source.neighbors
             if state.territories[nid].owner_id != pid),
            None,
        )
        if enemy_neighbor is None:
            pytest.skip("No enemy neighbor of 1-troop territory")

        with pytest.raises(GameActionError, match="at least 2 troops"):
            attack(state, pid, one_troop_source.id, enemy_neighbor.id, 1)

    def test_successful_attack_transfers_territory(self):
        """Force a win by using overwhelming troops."""
        state = make_match()
        state = get_to_attack_phase(state)
        pid = state.current_player_id
        source, target = find_attack_pair(state)
        if source is None:
            pytest.skip("No attackable pair")

        # Give source a massive troop advantage
        state.territories[source.id] = source.model_copy_update(troops=100)
        target_id = target.id

        # Run 20 attacks until one succeeds (very likely with 99 vs 1)
        won = False
        for _ in range(20):
            result_state = attack(state, pid, source.id, target_id, 99)
            if result_state.territories[target_id].owner_id == pid:
                won = True
                final_state = result_state
                break
            # Reset for next attempt (keep original state)

        assert won, "Expected to win at least once with 99 troops"
        assert final_state.territories[target_id].owner_id == pid
        assert final_state.territories[target_id].troops == 99

    def test_successful_attack_reduces_source_troops(self):
        state = make_match()
        state = get_to_attack_phase(state)
        pid = state.current_player_id
        source, target = find_attack_pair(state)
        if source is None:
            pytest.skip("No attackable pair")

        state.territories[source.id] = source.model_copy_update(troops=100)

        for _ in range(20):
            result = attack(state, pid, source.id, target.id, 99)
            if result.territories[target.id].owner_id == pid:
                assert result.territories[source.id].troops == 1
                return

        pytest.skip("Did not get a win in 20 tries")

    def test_failed_attack_keeps_territory_owner(self):
        state = make_match()
        state = get_to_attack_phase(state)
        pid = state.current_player_id
        source, target = find_attack_pair(state)
        if source is None:
            pytest.skip("No attackable pair")

        original_owner = target.owner_id
        state.territories[target.id] = target.model_copy_update(troops=100)
        state.territories[source.id] = source.model_copy_update(troops=5)

        for _ in range(20):
            result = attack(state, pid, source.id, target.id, 1)
            if not result.territories[target.id].owner_id == pid:
                assert result.territories[target.id].owner_id == original_owner
                return

        pytest.skip("All attacks won unexpectedly")

    def test_failed_attack_reduces_source_troops(self):
        state = make_match()
        state = get_to_attack_phase(state)
        pid = state.current_player_id
        source, target = find_attack_pair(state)
        if source is None:
            pytest.skip("No attackable pair")

        state.territories[target.id] = target.model_copy_update(troops=100)
        state.territories[source.id] = source.model_copy_update(troops=5)
        troops_before = 5

        for _ in range(20):
            result = attack(state, pid, source.id, target.id, 1)
            if result.territories[source.id].owner_id == pid:
                if not result.territories[target.id].owner_id == pid:
                    assert result.territories[source.id].troops == troops_before - 1
                    return

    def test_attack_logs_result(self):
        state = make_match()
        state = get_to_attack_phase(state)
        pid = state.current_player_id
        source, target = find_attack_pair(state)
        if source is None:
            pytest.skip("No attackable pair")

        state.territories[source.id] = source.model_copy_update(troops=10)
        result = attack(state, pid, source.id, target.id, 1)

        types = [e.type for e in result.action_log]
        assert "attack_success" in types or "attack_failed" in types

    def test_player_eliminated_when_loses_all_territories(self):
        """Verify elimination is detected when defender loses their last territory."""
        state = make_match()
        state = get_to_attack_phase(state)
        pid = state.current_player_id

        # Find the other player
        other_pid = [p for p in state.player_order if p != pid][0]
        other_territories = [
            t for t in state.territories.values() if t.owner_id == other_pid
        ]

        if len(other_territories) != 1:
            pytest.skip(
                f"Need exactly 1 territory for the defender, found {len(other_territories)}"
            )

        last_territory = other_territories[0]

        # Find an attacking territory adjacent to the defender's last
        source = next(
            (t for t in state.territories.values()
             if t.owner_id == pid and last_territory.id in t.neighbors),
            None,
        )
        if source is None:
            pytest.skip("No adjacent owned source for elimination test")

        state.territories[source.id] = source.model_copy_update(troops=100)
        state.territories[last_territory.id] = last_territory.model_copy_update(troops=1)

        won = False
        for _ in range(20):
            result = attack(state, pid, source.id, last_territory.id, 99)
            if result.territories[last_territory.id].owner_id == pid:
                won = True
                assert result.players[other_pid].eliminated
                types = [e.type for e in result.action_log]
                assert "player_eliminated" in types
                break

        if not won:
            pytest.skip("Could not force a win in 20 tries for elimination test")

    def test_multiple_attacks_in_same_phase(self):
        """Player can attack multiple times during the attack phase."""
        state = make_match()
        state = get_to_attack_phase(state)
        pid = state.current_player_id
        source, target = find_attack_pair(state)
        if source is None:
            pytest.skip("No attackable pair")

        state.territories[source.id] = source.model_copy_update(troops=50)

        # Attack twice
        state2 = attack(state, pid, source.id, target.id, 1)
        assert state2.phase == GamePhase.ATTACK  # still in attack phase

        source2, target2 = find_attack_pair(state2)
        if source2 is None:
            pytest.skip("No second attackable pair after first attack")
        state3 = attack(state2, pid, source2.id, target2.id, 1)
        assert state3.phase == GamePhase.ATTACK
