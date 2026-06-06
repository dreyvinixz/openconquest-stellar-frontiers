from __future__ import annotations

import random
from pydantic import BaseModel


class CombatResult(BaseModel):
    attacker_won: bool
    attack_roll: int
    defense_roll: int
    attack_power: int
    defense_power: int
    attacking_troops_sent: int
    attacking_troops_lost: int
    defending_troops_lost: int


def resolve_combat(attacking_troops: int, defending_troops: int, rng=None) -> CombatResult:
    if attacking_troops <= 0:
        raise ValueError("attacking_troops must be greater than zero")
    if defending_troops <= 0:
        raise ValueError("defending_troops must be greater than zero")

    rng = rng or random
    attack_roll = rng.randint(1, 6)
    defense_roll = rng.randint(1, 6)
    attack_power = attacking_troops + attack_roll
    defense_power = defending_troops + defense_roll
    attacker_won = attack_power > defense_power
    return CombatResult(
        attacker_won=attacker_won,
        attack_roll=attack_roll,
        defense_roll=defense_roll,
        attack_power=attack_power,
        defense_power=defense_power,
        attacking_troops_sent=attacking_troops,
        attacking_troops_lost=0 if attacker_won else attacking_troops,
        defending_troops_lost=defending_troops if attacker_won else 0,
    )


def win_probability(attacking_troops: int, defending_troops: int) -> float:
    if attacking_troops <= 0 or defending_troops <= 0:
        raise ValueError("attacking_troops and defending_troops must be greater than zero")
    wins = 0
    total = 36
    for attack_roll in range(1, 7):
        for defense_roll in range(1, 7):
            if attacking_troops + attack_roll > defending_troops + defense_roll:
                wins += 1
    return wins / total
