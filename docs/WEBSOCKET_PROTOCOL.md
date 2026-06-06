# WebSocket Protocol

All gameplay communication happens over WebSockets once a match starts.

## Connection
Endpoint: `ws://[host]/api/v1/matches/{match_id}/ws?token={player_token}`

## 1. Client to Server (Actions)

Clients send JSON payloads representing player actions. The server processes these via the Game Engine.

### `PlaceReinforcements`
Sent during the Reinforcement phase.
```json
{
  "type": "PlaceReinforcements",
  "payload": {
    "territory_id": "earth",
    "amount": 3
  }
}
```

### `Attack`
Sent during the Attack phase.
```json
{
  "type": "Attack",
  "payload": {
    "source_id": "earth",
    "target_id": "mars",
    "amount": 2
  }
}
```

### `MoveTroops`
Sent during the Movement phase.
```json
{
  "type": "MoveTroops",
  "payload": {
    "source_id": "earth",
    "target_id": "moon",
    "amount": 1
  }
}
```

### `EndPhase` / `EndTurn`
Advances the current phase or ends the turn.
```json
{
  "type": "EndPhase",
  "payload": {}
}
```

## 2. Server to Client (Events)

### `GameStateUpdate`
Broadcast to all players in the match whenever the state changes.
```json
{
  "type": "GameStateUpdate",
  "payload": {
    "match_id": "...",
    "phase": "attack",
    "current_player": "player-uuid",
    "territories": { ... },
    "logs": [ ... ]
  }
}
```

### `Error`
Sent to a specific client if their action was invalid.
```json
{
  "type": "Error",
  "payload": {
    "message": "Not enough fleets to attack."
  }
}
```

### `GameLog`
Broadcast to all players for UI activity feeds (e.g., combat results).
```json
{
  "type": "GameLog",
  "payload": {
    "message": "Player 1 conquered Mars from Player 2!"
  }
}
```
