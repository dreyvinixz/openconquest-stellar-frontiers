# Rules — OpenConquest: Stellar Frontiers MVP

## Setup

2 to 4 players join a room. When the host starts, the server distributes planets/stations, assigns secret missions and selects the first player.

## Turn Phases

1. Reinforcement
2. Attack
3. Movement
4. End turn

## Reinforcement

```text
base_fleets = max(3, floor(controlled_nodes / 3))
sector_bonus = sum bonus for each fully controlled sector
total = base_fleets + sector_bonus
```

All fleets must be placed before advancing to attack.

## Attack

The active player may attack adjacent enemy nodes from a controlled node with at least 2 fleets.

```text
attack_power = attacking_fleets + roll(1-6)
defense_power = defending_fleets + roll(1-6)
```

The attacker wins only if `attack_power > defense_power`; ties go to the defender.

## Movement

Once per turn, after the attack phase, the active player may move fleets between two adjacent controlled nodes. The source must keep at least 1 fleet.

## Victory

A player wins by completing their secret mission at the end of their turn or by becoming the last faction with controlled nodes.
