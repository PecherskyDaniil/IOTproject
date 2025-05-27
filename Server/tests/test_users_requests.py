from fastapi.testclient import TestClient
from .testdatabase import TestingSessionLocal
import random
from ..API.main import app,get_db

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


def test_user_create():
    response = client.post("/users/create",json={"name":"testuser","chat_id":"56223"})
    assert response.status_code == 200
    assert response.json()["name"] == "testuser"

def test_user_create_chat_id_error():
    response = client.post("/users/create",json={"name":"testusererror","chat_id":"56223"})
    assert response.status_code == 400
    assert response.json()["detail"] == "Chat already registered"

def test_get_users():
    response = client.get("/users")
    assert len(response.json())==1
    assert response.status_code == 200

def test_device_create():
    response = client.post("/devices/create",json={"unique_hash":"5263621","device_name":"testdevice","user_id":1})
    assert response.status_code == 200
    assert response.json()["name"] == "testdevice"

def test_device_create_hash_error():
    response = client.post("/devices/create",json={"unique_hash":"5263621","device_name":"testdeviceerror","user_id":1})
    assert response.status_code == 400
    assert response.json()["detail"] == "Hash already registered"

def test_get_devices():
    response = client.get("/devices")
    assert len(response.json())==1
    assert response.status_code == 200

def test_insert_device_data():
    response = client.post("/devices/data/update",json={"hash":"5263621","turbidity":22.2,"waterlevel":34.1})
    print(response.json())
    assert response.status_code == 200
    assert response.json()["name"] == "testdevice"

def test_feed_device_data():
    response = client.get("/devices/feed?hash=5263621")
    print(response.json())
    assert response.status_code == 200
    assert response.json()["feed_interval"] == 6
