# Architecture — OpenConquest: Stellar Frontiers

## Principle

The backend is the single source of truth. The frontend must never decide combat, ownership, phase progression, elimination or victory.

## Layers

```text
React/Vite frontend   -> REST/WebSocket -> FastAPI API/services
                                      -> pure game_engine
                                      -> persistence later
```

## Game Engine

Location: `apps/api/app/game_engine/`

The engine is pure Python and has no dependency on FastAPI or database code.

Modules:

- `state.py`: domain models and enums
- `map.py`: default galaxy map and graph validation
- `combat.py`: combat resolution and probability helper
- `objectives.py`: secret mission loading and checking
- `validators.py`: action validation
- `reducer.py`: state transitions

## Current Storage

Not implemented yet. MVP phase 2 should persist `MatchState` as JSON first, then normalize later.
