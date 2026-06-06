# Game Design — OpenConquest: Stellar Frontiers

## Concept

OpenConquest: Stellar Frontiers is a multiplayer turn-based space conquest game. Players command rival factions after the collapse of a central federation and compete to control planets, stations, jump gates and strategic galactic sectors.

## Core Loop

1. Receive fleet reinforcements.
2. Deploy fleets to controlled planets/stations.
3. Launch orbital invasions against connected enemy nodes.
4. Transfer fleets between adjacent controlled nodes.
5. End turn and check secret mission completion.

## MVP Theme Mapping

The game engine is generic and testable. The user-facing theme is space conquest.

- Territory = planet/station/orbital node
- Region = galactic sector
- Troops = fleets
- Attack = orbital invasion
- Objective = secret mission

## MVP Secret Missions

- Control at least 7 planets or stations.
- Fully control at least 2 galactic sectors.
- Fully control Iron Coast Sector and Sun Desert Sector.
- Eliminate at least one rival faction.

## Design Pillars

- Strategic map control
- High readability
- Short MVP rules
- Server-authoritative multiplayer
- Original identity, not a clone of any commercial board game
