"""
Tests: Turn system, end_turn, round progression, and objective victory.
"""

from __future__ import annotations

import pytest

from app.game_engine.objectives import (
    check_objective_completed,
    load_default_objectives,
)
from app.game_engine.reducer import (
    advance_phase,
    end_turn,
    place_reinforcement,
)
from app.game_engine.state import GamePhase
from app.game_engine.validators import GameActionError
from tests.conftest import make_match


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def get_to_attack_phase(state):
    pid = state.current_player_id
    pool = state.players[pid].reinforcement_pool
    if pool > 0:
        t = next(t for t in state.territories.values() if t.owner_id == pid)
        state = place_reinforcement(state, pid, t.id, pool)
    return advance_phase(state, pid)


def get_to_movement_phase(state):
    state = get_to_attack_phase(state)
    return advance_phase(state, state.current_player_id)


def complete_turn(state):
    """Move current player through all phases and end their turn."""
    state = get_to_movement_phase(state)
    return end_turn(state, state.current_player_id)


# ---------------------------------------------------------------------------
# Turn system tests
# ---------------------------------------------------------------------------


class TestEndTurn:
    def test_end_turn_changes_current_player(self):
        state = make_match()
        first_pid = state.current_player_id
        state = complete_turn(state)
        assert state.current_player_id != first_pid

    def test_end_turn_new_player_gets_reinforcement_pool(self):
        state = make_match()
        state = complete_turn(state)
        new_pid = state.current_player_id
        assert state.players[new_pid].reinforcement_pool >= 3

    def test_end_turn_phase_returns_to_reinforcement(self):
        state = make_match()
        state = complete_turn(state)
        assert state.phase == GamePhase.REINFORCEMENT

    def test_end_turn_requires_attack_or_movement_phase(self):
        state = make_match()
        pid = state.current_player_id
        # Still in reinforcement — cannot end turn
        with pytest.raises(GameActionError):
            end_turn(state, pid)

    def test_end_turn_requires_current_player(self):
        state = make_match()
        state = get_to_attack_phase(state)
        pid = state.current_player_id
        other_pid = [p for p in state.player_order if p != pid][0]
        with pytest.raises(GameActionError, match="not your turn"):
            end_turn(state, other_pid)

    def test_eliminated_player_skipped_in_turn_order(self):
        """When a player is eliminated, their turns are skipped."""
        state = make_match()
        # Manually eliminate one player
        pid = state.current_player_id
        other_pid = [p for p in state.player_order if p != pid][0]
        state.players[other_pid] = state.players[other_pid].model_copy_update(
            eliminated=True
        )
        # Remove their territories
        for tid, t in state.territories.items():
            if t.owner_id == other_pid:
                state.territories[tid] = t.model_copy_update(owner_id=pid)

        state = complete_turn(state)
        # Should skip other_pid and either wrap or be only player
        assert state.current_player_id != other_pid

    def test_round_number_increments_after_full_round(self):
        state = make_match()
        n_players = len(state.player_order)
        initial_round = state.round_number

        for _ in range(n_players):
            state = complete_turn(state)

        assert state.round_number == initial_round + 1

    def test_turn_started_log_entry_added(self):
        state = make_match()
        state = complete_turn(state)
        types = [e.type for e in state.action_log]
        assert "turn_started" in types

    def test_turn_ended_log_entry_added(self):
        state = make_match()
        state = get_to_movement_phase(state)
        pid = state.current_player_id
        state = end_turn(state, pid)
        types = [e.type for e in state.action_log]
        assert "turn_ended" in types

    def test_previous_player_reinforcement_pool_reset(self):
        """After turn ends, the previous player's pool should be 0."""
        state = make_match()
        first_pid = state.current_player_id
        state = complete_turn(state)
        assert state.players[first_pid].reinforcement_pool == 0

    def test_conquered_this_turn_resets_on_new_turn(self):
        state = make_match()
        first_pid = state.current_player_id
        state.players[first_pid] = state.players[first_pid].model_copy_update(
            territories_conquered_this_turn=3
        )
        state = complete_turn(state)
        # Next player should have 0
        assert state.players[state.current_player_id].territories_conquered_this_turn == 0


# ---------------------------------------------------------------------------
# Objective tests
# ---------------------------------------------------------------------------


class TestObjectives:
    def test_objectives_loaded(self):
        objectives = load_default_objectives()
        assert len(objectives) == 4

    def test_control_territory_count_objective(self):
        state = make_match()
        pid = state.current_player_id

        # Set objective to control_7_territories
        state.players[pid] = state.players[pid].model_copy_update(
            objective_id="control_7_territories"
        )

        # Give player 7 territories
        count = 0
        for tid, t in state.territories.items():
            if count < 7:
                state.territories[tid] = t.model_copy_update(owner_id=pid)
                count += 1
            else:
                other_pid = [p for p in state.player_order if p != pid][0]
                state.territories[tid] = t.model_copy_update(owner_id=other_pid)

        assert check_objective_completed(state, pid)

    def test_control_territory_count_objective_fails_below_threshold(self):
        state = make_match()
        pid = state.current_player_id
        state.players[pid] = state.players[pid].model_copy_update(
            objective_id="control_7_territories"
        )

        # Give player only 5 territories
        other_pid = [p for p in state.player_order if p != pid][0]
        count = 0
        for tid, t in state.territories.items():
            if count < 5:
                state.territories[tid] = t.model_copy_update(owner_id=pid)
                count += 1
            else:
                state.territories[tid] = t.model_copy_update(owner_id=other_pid)

        assert not check_objective_completed(state, pid)

    def test_control_2_regions_objective(self):
        state = make_match()
        pid = state.current_player_id
        state.players[pid] = state.players[pid].model_copy_update(
            objective_id="control_2_regions"
        )
        other_pid = [p for p in state.player_order if p != pid][0]

        # Give player all of northlands and iron_coast
        for region_id in ["northlands", "iron_coast"]:
            region = state.regions[region_id]
            for tid in region.territory_ids:
                state.territories[tid] = state.territories[tid].model_copy_update(
                    owner_id=pid
                )

        # Give remaining to other player
        controlled = {
            tid
            for r in ["northlands", "iron_coast"]
            for tid in state.regions[r].territory_ids
        }
        for tid in state.territories:
            if tid not in controlled:
                state.territories[tid] = state.territories[tid].model_copy_update(
                    owner_id=other_pid
                )

        assert check_objective_completed(state, pid)

    def test_control_2_regions_fails_with_only_1(self):
        state = make_match()
        pid = state.current_player_id
        state.players[pid] = state.players[pid].model_copy_update(
            objective_id="control_2_regions"
        )
        other_pid = [p for p in state.player_order if p != pid][0]

        # Give only northlands to player
        for tid in state.regions["northlands"].territory_ids:
            state.territories[tid] = state.territories[tid].model_copy_update(
                owner_id=pid
            )
        for tid in state.territories:
            if tid not in state.regions["northlands"].territory_ids:
                state.territories[tid] = state.territories[tid].model_copy_update(
                    owner_id=other_pid
                )

        assert not check_objective_completed(state, pid)

    def test_control_specific_regions_objective(self):
        state = make_match()
        pid = state.current_player_id
        state.players[pid] = state.players[pid].model_copy_update(
            objective_id="control_iron_and_sun"
        )
        other_pid = [p for p in state.player_order if p != pid][0]

        required = ["iron_coast", "sun_desert"]
        required_tids = {
            tid for r in required for tid in state.regions[r].territory_ids
        }

        for tid in state.territories:
            owner = pid if tid in required_tids else other_pid
            state.territories[tid] = state.territories[tid].model_copy_update(
                owner_id=owner
            )

        assert check_objective_completed(state, pid)

    def test_control_specific_regions_fails_if_missing_one(self):
        state = make_match()
        pid = state.current_player_id
        state.players[pid] = state.players[pid].model_copy_update(
            objective_id="control_iron_and_sun"
        )
        other_pid = [p for p in state.player_order if p != pid][0]

        # Only give iron_coast, not sun_desert
        for tid in state.regions["iron_coast"].territory_ids:
            state.territories[tid] = state.territories[tid].model_copy_update(
                owner_id=pid
            )
        for tid in state.territories:
            if tid not in state.regions["iron_coast"].territory_ids:
                state.territories[tid] = state.territories[tid].model_copy_update(
                    owner_id=other_pid
                )

        assert not check_objective_completed(state, pid)

    def test_eliminate_player_objective(self):
        state = make_match()
        pid = state.current_player_id
        state.players[pid] = state.players[pid].model_copy_update(
            objective_id="eliminate_one_player"
        )
        other_pid = [p for p in state.player_order if p != pid][0]

        # Eliminate the other player
        state.players[other_pid] = state.players[other_pid].model_copy_update(
            eliminated=True
        )

        assert check_objective_completed(state, pid)

    def test_eliminate_player_objective_fails_with_no_elimination(self):
        state = make_match()
        pid = state.current_player_id
        state.players[pid] = state.players[pid].model_copy_update(
            objective_id="eliminate_one_player"
        )
        # No one eliminated
        assert not check_objective_completed(state, pid)

    def test_eliminated_player_cannot_win(self):
        state = make_match()
        pid = state.current_player_id
        state.players[pid] = state.players[pid].model_copy_update(
            objective_id="control_7_territories",
            eliminated=True,
        )
        # Give player 13 territories
        for tid in state.territories:
            state.territories[tid] = state.territories[tid].model_copy_update(
                owner_id=pid
            )
        assert not check_objective_completed(state, pid)

    def test_player_with_no_objective_cannot_win(self):
        state = make_match()
        pid = state.current_player_id
        state.players[pid] = state.players[pid].model_copy_update(
            objective_id=None
        )
        assert not check_objective_completed(state, pid)


# ---------------------------------------------------------------------------
# Victory detection via end_turn
# ---------------------------------------------------------------------------


class TestVictoryDetection:
    def test_match_finishes_when_objective_met_at_end_turn(self):
        state = make_match()
        pid = state.current_player_id
        other_pid = [p for p in state.player_order if p != pid][0]

        # Set objective to control 7 territories
        state.players[pid] = state.players[pid].model_copy_update(
            objective_id="control_7_territories"
        )

        # Give player 7 territories, other player 6
        tids = list(state.territories.keys())
        for i, tid in enumerate(tids):
            owner = pid if i < 7 else other_pid
            state.territories[tid] = state.territories[tid].model_copy_update(
                owner_id=owner
            )

        # Get to a phase where end_turn is allowed
        state = get_to_movement_phase(state)
        state = end_turn(state, pid)

        assert state.phase == GamePhase.FINISHED
        assert state.winner_player_id == pid

    def test_match_finishes_when_last_player_standing(self):
        """If only one player has territories, they win."""
        state = make_match()
        pid = state.current_player_id
        other_pid = [p for p in state.player_order if p != pid][0]

        # Give all territories to current player
        for tid in state.territories:
            state.territories[tid] = state.territories[tid].model_copy_update(
                owner_id=pid
            )

        # Eliminate other player
        state.players[other_pid] = state.players[other_pid].model_copy_update(
            eliminated=True
        )

        state = get_to_movement_phase(state)
        state = end_turn(state, pid)

        assert state.phase == GamePhase.FINISHED
        assert state.winner_player_id == pid

    def test_match_finished_action_logged(self):
        state = make_match()
        pid = state.current_player_id
        other_pid = [p for p in state.player_order if p != pid][0]

        state.players[pid] = state.players[pid].model_copy_update(
            objective_id="control_7_territories"
        )
        tids = list(state.territories.keys())
        for i, tid in enumerate(tids):
            state.territories[tid] = state.territories[tid].model_copy_update(
                owner_id=(pid if i < 7 else other_pid)
            )

        state = get_to_movement_phase(state)
        state = end_turn(state, pid)

        types = [e.type for e in state.action_log]
        assert "match_finished" in types

    def test_match_continues_when_objective_not_met(self):
        state = make_match()
        pid = state.current_player_id

        # Assign an objective that isn't met
        state.players[pid] = state.players[pid].model_copy_update(
            objective_id="control_7_territories"
        )
        # Player has at most ~7 territories in a 2-player match with 13 territories
        # If they have 6, they should NOT win
        owned = [t for t in state.territories.values() if t.owner_id == pid]
        if len(owned) >= 7:
            pytest.skip("Player happens to already have 7+ territories")

        state = get_to_movement_phase(state)
        state = end_turn(state, pid)

        assert state.phase != GamePhase.FINISHED
        assert state.winner_player_id is None
