# Next Tasks for Development IA

## Phase 1 — Stabilize Engine

- Run all tests.
- Add tests for map graph validation.
- Add tests for 3 and 4 player match setup.
- Replace remaining user-facing `troop` strings with theme labels at API/UI layer only.

## Phase 2 — REST API

- Implement room creation.
- Implement join room.
- Implement start match.
- Implement get match state.

## Phase 3 — WebSocket

- Add connection manager by room code.
- Add action dispatch for reinforcement, attack, movement, phase advance and end turn.
- Broadcast `match_state_updated`.

## Phase 4 — Frontend

- Create Vite React app.
- Add lobby and room screens.
- Add SVG galaxy map.
- Add action panel.
