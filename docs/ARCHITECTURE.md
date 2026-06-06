# Architecture — OpenConquest: Stellar Frontiers

## Overview
OpenConquest is built with a strictly separated architecture. The backend serves as the absolute source of truth. The frontend is a thin client that displays the state and sends user actions.

## Layers

### 1. Game Engine Layer (`game_engine/`)
The core of the game. It is designed as a **pure function state machine**:
- Takes the current `GameState` and an `Action`.
- Returns a new `GameState` or raises an exception if the action is invalid.
- **Zero side-effects:** No database calls, no network requests, no asyncio.
- **Deterministic:** Given the same state and action, it produces the exact same new state. Randomness (e.g., in combat) is handled by passing a seeded random generator or resolving rolls clearly in a dedicated combat module.

### 2. Service Layer (`services/`)
Orchestrates the application logic. 
- Loads the game state from the database.
- Passes user actions to the Game Engine.
- Saves the updated state back to the database.
- Handles authorization and room lifecycle (creating, joining, starting matches).

### 3. Transport Layer (`routers/` & `websocket/`)
The interface to the outside world, powered by **FastAPI**.
- **REST API:** Handles state-agnostic operations like authentication, lobby management, and room creation.
- **WebSocket:** Handles realtime match communication. Subscribes to match channels, sends player actions to the Service layer, and broadcasts `GameStateUpdate` events.

### 4. Data Layer (`database.py` & `models/`)
Stores persistent state (e.g., PostgreSQL).
- **Match State:** The complex game board state is stored as a structured `JSON` column. This perfectly matches the `pydantic` models of the Game Engine, avoiding complex ORM mapping for deeply nested game structures.

### 5. Frontend Layer (`apps/web/`)
A React/Vite application.
- Holds local state in stores (e.g., Zustand).
- Synchronizes local state with server state via WebSocket events.
- Never computes game logic directly—it only renders the `GameState` it receives.
