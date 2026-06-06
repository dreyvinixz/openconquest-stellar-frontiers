# REST API Specification

This document defines the REST endpoints for managing the lobby and rooms. Real-time game events happen over WebSocket.

## Base URL
`/api/v1`

---

## Rooms (Lobby)

### `GET /rooms`
List all active public rooms waiting for players.
- **Response**: `200 OK`
  ```json
  [
    {
      "id": "room-uuid",
      "name": "Alpha Sector Skirmish",
      "players": 2,
      "max_players": 4,
      "status": "waiting"
    }
  ]
  ```

### `POST /rooms`
Create a new room.
- **Payload**:
  ```json
  {
    "name": "Alpha Sector Skirmish",
    "max_players": 4,
    "map_id": "default_galaxy"
  }
  ```
- **Response**: `201 Created`
  ```json
  {
    "id": "room-uuid",
    "name": "Alpha Sector Skirmish",
    "status": "waiting",
    "host_token": "player-secret-token"
  }
  ```

### `POST /rooms/{room_id}/join`
Join an existing room.
- **Payload**:
  ```json
  {
    "player_name": "Commander Shepard"
  }
  ```
- **Response**: `200 OK`
  ```json
  {
    "player_id": "player-uuid",
    "player_token": "player-secret-token"
  }
  ```

### `POST /rooms/{room_id}/start`
Start the match (Host only).
- **Headers**: `Authorization: Bearer {host_token}`
- **Response**: `200 OK`
  ```json
  {
    "match_id": "match-uuid"
  }
  ```
