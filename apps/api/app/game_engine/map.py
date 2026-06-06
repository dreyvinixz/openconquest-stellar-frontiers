from __future__ import annotations

from .state import Region, Territory


DEFAULT_TERRITORIES_RAW = {
    "N1": {"id": "N1", "name": "Helios Gate", "region": "northlands", "terrain": "jump_gate", "neighbors": ["N2", "C1"], "x": 20, "y": 20},
    "N2": {"id": "N2", "name": "Frost Relay", "region": "northlands", "terrain": "ice_world", "neighbors": ["N1", "N3", "C2"], "x": 40, "y": 18},
    "N3": {"id": "N3", "name": "White Harbor Station", "region": "northlands", "terrain": "orbital_station", "neighbors": ["N2", "I1"], "x": 60, "y": 20},
    "I1": {"id": "I1", "name": "Iron Port", "region": "iron_coast", "terrain": "shipyard", "neighbors": ["N3", "I2", "C3"], "x": 75, "y": 35},
    "I2": {"id": "I2", "name": "Steel Bay Colony", "region": "iron_coast", "terrain": "industrial_world", "neighbors": ["I1", "I3"], "x": 82, "y": 55},
    "I3": {"id": "I3", "name": "Black Cliff Outpost", "region": "iron_coast", "terrain": "fortress_moon", "neighbors": ["I2", "S3"], "x": 72, "y": 75},
    "C1": {"id": "C1", "name": "Greenfield Prime", "region": "central_plains", "terrain": "terraformed_world", "neighbors": ["N1", "C2", "S1"], "x": 25, "y": 45},
    "C2": {"id": "C2", "name": "Rivercross Nebula", "region": "central_plains", "terrain": "nebula", "neighbors": ["N2", "C1", "C3", "S2"], "x": 45, "y": 45},
    "C3": {"id": "C3", "name": "Stonebridge Station", "region": "central_plains", "terrain": "trade_hub", "neighbors": ["C2", "C4", "I1"], "x": 60, "y": 48},
    "C4": {"id": "C4", "name": "Old Road Beacon", "region": "central_plains", "terrain": "beacon", "neighbors": ["C3", "S3"], "x": 55, "y": 65},
    "S1": {"id": "S1", "name": "Sunwatch Colony", "region": "sun_desert", "terrain": "solar_world", "neighbors": ["C1", "S2"], "x": 25, "y": 78},
    "S2": {"id": "S2", "name": "Amber Belt", "region": "sun_desert", "terrain": "asteroid_belt", "neighbors": ["S1", "C2", "S3"], "x": 42, "y": 82},
    "S3": {"id": "S3", "name": "Red Oasis Station", "region": "sun_desert", "terrain": "oasis_station", "neighbors": ["S2", "C4", "I3"], "x": 60, "y": 85},
}

DEFAULT_REGIONS_RAW = {
    "northlands": {"id": "northlands", "name": "Helios Fringe", "bonus_troops": 2, "territory_ids": ["N1", "N2", "N3"]},
    "iron_coast": {"id": "iron_coast", "name": "Iron Coast Sector", "bonus_troops": 2, "territory_ids": ["I1", "I2", "I3"]},
    "central_plains": {"id": "central_plains", "name": "Central Trade Spine", "bonus_troops": 3, "territory_ids": ["C1", "C2", "C3", "C4"]},
    "sun_desert": {"id": "sun_desert", "name": "Sun Desert Sector", "bonus_troops": 2, "territory_ids": ["S1", "S2", "S3"]},
}


def load_default_map() -> tuple[dict[str, Territory], dict[str, Region]]:
    territories = {tid: Territory(**data) for tid, data in DEFAULT_TERRITORIES_RAW.items()}
    regions = {rid: Region(**data) for rid, data in DEFAULT_REGIONS_RAW.items()}
    validate_map_graph(territories)
    validate_regions(territories, regions)
    return territories, regions


def validate_map_graph(territories: dict[str, Territory]) -> None:
    for tid, territory in territories.items():
        for neighbor_id in territory.neighbors:
            if neighbor_id not in territories:
                raise ValueError(f"Territory {tid} has unknown neighbor {neighbor_id}")
            if tid not in territories[neighbor_id].neighbors:
                raise ValueError(f"Neighbor relationship {tid}<->{neighbor_id} is not symmetric")


def validate_regions(territories: dict[str, Territory], regions: dict[str, Region]) -> None:
    for rid, region in regions.items():
        for tid in region.territory_ids:
            if tid not in territories:
                raise ValueError(f"Region {rid} references unknown territory {tid}")
            if territories[tid].region != rid:
                raise ValueError(f"Territory {tid} region mismatch: {territories[tid].region} != {rid}")
