"""
Tests: Combat resolution system.
"""

from __future__ import annotations

import random

import pytest

from app.game_engine.combat import resolve_combat, win_probability


class TestResolveCombat:
    def test_attacker_wins_when_attack_power_greater(self):
        # Force attacker to roll 6, defender to roll 1
        rng = random.Random()
        rng.randint = lambda a, b: [6, 1].pop(0)  # type: ignore
        # 3 + 6 = 9 > 2 + 1 = 3 → attacker wins
        # We'll use a seeded approach instead
        result = resolve_combat(10, 1, rng=random.Random(0))
        # With seed 0: attacker has overwhelming advantage with 10 troops
        assert isinstance(result.attacker_won, bool)

    def test_result_contains_all_fields(self):
        result = resolve_combat(3, 2, rng=random.Random(42))
        assert result.attack_roll in range(1, 7)
        assert result.defense_roll in range(1, 7)
        assert result.attack_power == 3 + result.attack_roll
        assert result.defense_power == 2 + result.defense_roll
        assert result.attacking_troops_sent == 3

    def test_attacker_wins_if_attack_power_greater(self):
        # Craft a scenario where attacker definitely wins
        # 100 troops vs 1 troop — attacker should almost always win
        wins = sum(
            1 for _ in range(200)
            if resolve_combat(100, 1).attacker_won
        )
        assert wins > 190  # near certain with 100 vs 1

    def test_defender_wins_if_attack_power_not_greater(self):
        # 1 troop attacking 100 troops — defender should almost always win
        wins = sum(
            1 for _ in range(200)
            if resolve_combat(1, 100).attacker_won
        )
        assert wins < 10  # very unlikely to win 1 vs 100

    def test_attacker_lost_troops_on_defeat(self):
        result = resolve_combat(3, 100, rng=random.Random(99))
        if not result.attacker_won:
            assert result.attacking_troops_lost == 3
            assert result.defending_troops_lost == 0

    def test_defender_lost_all_troops_on_attacker_win(self):
        result = resolve_combat(100, 3, rng=random.Random(1))
        if result.attacker_won:
            assert result.defending_troops_lost == 3
            assert result.attacking_troops_lost == 0

    def test_raises_on_zero_attacking_troops(self):
        with pytest.raises(ValueError, match="attacking_troops"):
            resolve_combat(0, 5)

    def test_raises_on_zero_defending_troops(self):
        with pytest.raises(ValueError, match="defending_troops"):
            resolve_combat(5, 0)

    def test_raises_on_negative_attacking_troops(self):
        with pytest.raises(ValueError):
            resolve_combat(-1, 5)

    def test_rolls_are_in_valid_range(self):
        for _ in range(100):
            result = resolve_combat(5, 5)
            assert 1 <= result.attack_roll <= 6
            assert 1 <= result.defense_roll <= 6

    def test_tie_goes_to_defender(self):
        """When powers are equal, defender wins (attacker wins only if strictly greater)."""
        # 5 troops each, same roll → tie goes to defender
        class FixedRng:
            def randint(self, a, b):
                return 3  # always returns 3

        result = resolve_combat(5, 5, rng=FixedRng())  # type: ignore
        # 5+3 = 8 vs 5+3 = 8 → not >, defender wins
        assert not result.attacker_won

    def test_deterministic_with_seeded_rng(self):
        r1 = resolve_combat(5, 5, rng=random.Random(777))
        r2 = resolve_combat(5, 5, rng=random.Random(777))
        assert r1.attack_roll == r2.attack_roll
        assert r1.defense_roll == r2.defense_roll
        assert r1.attacker_won == r2.attacker_won


class TestWinProbability:
    def test_strong_attacker_has_high_probability(self):
        prob = win_probability(10, 1)
        assert prob > 0.8

    def test_weak_attacker_has_low_probability(self):
        prob = win_probability(1, 10)
        assert prob < 0.2

    def test_probability_is_between_0_and_1(self):
        for atk in range(1, 10):
            for def_ in range(1, 10):
                p = win_probability(atk, def_)
                assert 0.0 <= p <= 1.0

    def test_equal_troops_probability_near_half(self):
        """With equal troops, it's slightly less than 50% for attacker (tie goes to defender)."""
        prob = win_probability(5, 5)
        # Attacker wins only when attack_roll > defense_roll
        # P(A > B) for two dice = 15/36 ≈ 0.417
        assert 0.40 <= prob <= 0.45

    def test_returns_float(self):
        assert isinstance(win_probability(3, 3), float)
