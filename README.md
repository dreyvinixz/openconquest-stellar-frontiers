# OpenConquest: Stellar Frontiers

OpenConquest: Stellar Frontiers is an open-source turn-based space conquest strategy game with online multiplayer rooms, modular galaxy maps, secret missions, fleet combat and a server-authoritative game engine.

The current ZIP contains the first backend/game-engine scaffold and tests. The frontend, persistence and WebSocket layers are intentionally left as next implementation phases.

## Legal Notice

OpenConquest: Stellar Frontiers is an independent open-source project. It is not affiliated with, endorsed by, or connected to Grow, WAR, Risk, Hasbro, or any other commercial board game publisher.

All names, maps, sectors, planets, stations, rules, assets and mechanics in this project are original or based on generic concepts of the territory-control and space-strategy genres.

## MVP Features Implemented

- Pure Python game engine
- Deterministic default galaxy map
- Player state, sectors, planet/station nodes and objectives
- Reinforcement phase
- Attack phase with fleet combat
- Movement phase
- Turn progression
- Objective checking
- Elimination and victory detection
- Unit tests for combat, reinforcement, attack, movement, turns and objectives
- Minimal FastAPI health endpoint

## Tech Stack

- Python 3.12+
- FastAPI
- Pydantic v2
- Pytest
- Docker-ready API scaffold

## Run Locally

```bash
cd apps/api
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
pytest -v
uvicorn app.main:app --reload
```

Health check:

```bash
curl http://localhost:8000/api/v1/health
```

## Project Structure

```text
openconquest-stellar-frontiers/
├── apps/
│   └── api/
│       ├── app/
│       │   ├── game_engine/
│       │   │   ├── state.py
│       │   │   ├── map.py
│       │   │   ├── combat.py
│       │   │   ├── objectives.py
│       │   │   ├── validators.py
│       │   │   └── reducer.py
│       │   ├── routers/
│       │   └── main.py
│       └── tests/
├── docs/
├── docker-compose.yml
├── .env.example
└── README.md
```

## Current Architecture Decision

The engine still uses generic internal names like `Territory`, `Region` and `troops` so the rules remain theme-agnostic and easy to test. In the Stellar Frontiers UI/theme, these map to:

| Engine term | Space theme term |
|---|---|
| Territory | Planet / station / orbital node |
| Region | Galactic sector |
| Troops | Fleets |
| Attack | Orbital invasion |
| Objective | Secret mission |

## Next Steps

1. Finish REST room and match services.
2. Add WebSocket room channels.
3. Add PostgreSQL state persistence.
4. Build React/Vite frontend with SVG galaxy map.
5. Add lobby, room page and match page.
