from __future__ import annotations

from .state import MatchState, Objective, ObjectiveType


def load_default_objectives() -> dict[str, Objective]:
    return {
        "control_7_territories": Objective(
            id="control_7_territories",
            title="Expansion Doctrine",
            description="Control at least 7 planets or stations at the end of your turn.",
            type=ObjectiveType.CONTROL_TERRITORY_COUNT,
            params={"count": 7},
        ),
        "control_2_regions": Objective(
            id="control_2_regions",
            title="Sector Command",
            description="Fully control at least 2 galactic sectors at the end of your turn.",
            type=ObjectiveType.CONTROL_REGION_COUNT,
            params={"count": 2},
        ),
        "control_iron_and_sun": Objective(
            id="control_iron_and_sun",
            title="Coast to Starfire",
            description="Fully control the Iron Coast Sector and the Sun Desert Sector.",
            type=ObjectiveType.CONTROL_SPECIFIC_REGIONS,
            params={"regions": ["iron_coast", "sun_desert"]},
        ),
        "eliminate_one_player": Objective(
            id="eliminate_one_player",
            title="Decisive Strike",
            description="Eliminate at least one rival faction.",
            type=ObjectiveType.ELIMINATE_PLAYER_COUNT,
            params={"count": 1},
        ),
    }


def player_territory_count(state: MatchState, player_id: str) -> int:
    return sum(1 for t in state.territories.values() if t.owner_id == player_id)


def controlled_regions(state: MatchState, player_id: str) -> list[str]:
    controlled: list[str] = []
    for region_id, region in state.regions.items():
        if all(state.territories[tid].owner_id == player_id for tid in region.territory_ids):
            controlled.append(region_id)
    return controlled


def check_objective_completed(state: MatchState, player_id: str) -> bool:
    player = state.players.get(player_id)
    if player is None or player.eliminated or not player.objective_id:
        return False
    objective = state.objectives.get(player.objective_id)
    if objective is None:
        return False

    objective_type = objective.type.value if hasattr(objective.type, "value") else str(objective.type)
    if objective_type == ObjectiveType.CONTROL_TERRITORY_COUNT.value:
        return player_territory_count(state, player_id) >= int(objective.params.get("count", 0))
    if objective_type == ObjectiveType.CONTROL_REGION_COUNT.value:
        return len(controlled_regions(state, player_id)) >= int(objective.params.get("count", 0))
    if objective_type == ObjectiveType.CONTROL_SPECIFIC_REGIONS.value:
        required = objective.params.get("regions", [])
        owned = set(controlled_regions(state, player_id))
        return all(region_id in owned for region_id in required)
    if objective_type == ObjectiveType.ELIMINATE_PLAYER_COUNT.value:
        count = int(objective.params.get("count", 1))
        if player.players_eliminated >= count:
            return True
        eliminated_others = sum(1 for pid, p in state.players.items() if pid != player_id and p.eliminated)
        return eliminated_others >= count
    return False
