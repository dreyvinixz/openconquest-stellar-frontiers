# Security Policy

## Reporting a Vulnerability

If you discover any security related issues, please email the maintainers instead of using the public issue tracker. 

### In-Game Security
- **State Manipulation:** The game engine operates exclusively on the backend. Client-side state is strictly visual. All actions are validated against the current server state.
- **WebSocket Hijacking:** WebSocket connections require a `player_token` issued upon joining a room. Connections without a valid token are rejected.
- **Rate Limiting:** TBD for REST endpoints to prevent spamming room creation.

## Dependency Management
We use Dependabot to monitor python and node dependencies. Ensure any new dependencies introduced are actively maintained and free of known CVEs.
