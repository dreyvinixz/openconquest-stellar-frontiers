# Product Direction

## Vision
OpenConquest: Stellar Frontiers aims to be a highly accessible, fast-paced browser-based strategy game. It captures the thrill of territorial conquest board games while eliminating the physical setup time and manual rule enforcement.

## Target Audience
- Strategy game enthusiasts.
- Groups of friends looking for async or realtime online matches.
- Open-source developers looking for a clean, understandable game architecture.

## Guiding Principles
1. **No Clones:** We draw inspiration from the territory-control genre but establish our own spatial identity.
2. **Server-Authoritative:** The backend dictates the rules. Cheating on the client is impossible.
3. **Purity over Convenience:** The game engine must remain unaware of the transport layer (no FastAPI, no websockets in the engine module).
4. **Testability:** Every combat scenario, reinforcement calculation, and objective check must have an automated test.
