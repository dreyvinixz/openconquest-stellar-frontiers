from fastapi.testclient import TestClient
from app.main import app
from app.services.room_service import _rooms_db, _matches_db

client = TestClient(app)

def setup_function():
    # Clear in-memory db before each test
    _rooms_db.clear()
    _matches_db.clear()

def test_create_room():
    response = client.post("/api/v1/rooms", json={
        "player_name": "HostPlayer",
        "max_players": 4
    })
    assert response.status_code == 201
    data = response.json()
    assert "room_code" in data
    assert "player_id" in data
    assert "player_token" in data

def test_get_room():
    create_res = client.post("/api/v1/rooms", json={"player_name": "HostPlayer"})
    room_code = create_res.json()["room_code"]
    
    response = client.get(f"/api/v1/rooms/{room_code}")
    assert response.status_code == 200
    data = response.json()
    assert data["room_code"] == room_code
    assert len(data["players"]) == 1
    assert data["players"][0]["name"] == "HostPlayer"
    assert data["players"][0]["is_host"] is True

def test_join_room():
    create_res = client.post("/api/v1/rooms", json={"player_name": "HostPlayer"})
    room_code = create_res.json()["room_code"]
    
    join_res = client.post(f"/api/v1/rooms/{room_code}/join", json={"player_name": "Player2"})
    assert join_res.status_code == 200
    data = join_res.json()
    assert "player_token" in data
    
    room_res = client.get(f"/api/v1/rooms/{room_code}")
    assert len(room_res.json()["players"]) == 2

def test_start_match_requires_host():
    create_res = client.post("/api/v1/rooms", json={"player_name": "HostPlayer"})
    room_code = create_res.json()["room_code"]
    
    join_res = client.post(f"/api/v1/rooms/{room_code}/join", json={"player_name": "Player2"})
    p2_token = join_res.json()["player_token"]
    
    start_res = client.post(
        f"/api/v1/rooms/{room_code}/start",
        headers={"Authorization": f"Bearer {p2_token}"}
    )
    assert start_res.status_code == 403

def test_start_match_success():
    create_res = client.post("/api/v1/rooms", json={"player_name": "HostPlayer"})
    host_token = create_res.json()["player_token"]
    room_code = create_res.json()["room_code"]
    
    client.post(f"/api/v1/rooms/{room_code}/join", json={"player_name": "Player2"})
    
    start_res = client.post(
        f"/api/v1/rooms/{room_code}/start",
        headers={"Authorization": f"Bearer {host_token}"}
    )
    assert start_res.status_code == 200
    assert "match_id" in start_res.json()
    
    # Room status should be started
    room_res = client.get(f"/api/v1/rooms/{room_code}")
    assert room_res.json()["status"] == "started"

def test_cannot_join_full_room():
    create_res = client.post("/api/v1/rooms", json={"player_name": "P1", "max_players": 2})
    room_code = create_res.json()["room_code"]
    
    res2 = client.post(f"/api/v1/rooms/{room_code}/join", json={"player_name": "P2"})
    assert res2.status_code == 200
    
    res3 = client.post(f"/api/v1/rooms/{room_code}/join", json={"player_name": "P3"})
    assert res3.status_code == 400
    assert "full" in res3.json()["detail"].lower()
