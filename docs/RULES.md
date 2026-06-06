# Game Rules

This document maps the abstract game engine rules to the space theme of Stellar Frontiers.

## Game Board
The galaxy map consists of **Nodes** (planets, stations) grouped into **Sectors** (regions).
- Nodes are connected by jump lanes (adjacency).
- Fleets (troops) are stationed at these nodes.

## Phases of a Turn

### 1. Reinforcement Phase
At the beginning of a turn, the active player receives new fleets based on the nodes they control.
- **Base calculation:** Number of controlled nodes divided by 3 (minimum 3).
- **Sector Bonus:** If a player controls *every* node in a Sector, they receive bonus fleets specific to that Sector.
- The player places these fleets on any nodes they already control.

### 2. Attack Phase (Orbital Invasions)
The player can launch attacks from their controlled nodes to adjacent enemy nodes.
- **Requirement:** The attacking node must have at least 2 fleets (1 must stay behind).
- **Combat Resolution:** Dice rolls or deterministic strength comparison (depending on configuration) resolves the combat. If the attacker wins, they conquer the node and move at least the attacking fleets into it.

### 3. Movement Phase
The player can move fleets between connected nodes they control.
- **Requirement:** Must leave at least 1 fleet behind on the origin node.
- Typically limited to one movement action per turn, or limited by path adjacency.

## Secret Missions (Objectives)
Each player receives a secret mission at the start of the game.
- Example: "Control 2 entire Sectors" or "Eliminate the Red Faction".
- The game checks objective completion at the end of every turn. If met, the player wins the game.
