from __future__ import annotations

from app.game_engine.reducer import start_match


def make_match():
    """Create a deterministic two-player match for engine tests."""
    return start_match(player_names=['Andrey', 'Maria'], room_code='TEST01')
