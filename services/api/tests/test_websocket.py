import json
from starlette.testclient import TestClient
from app.main import app
from app.core.security import create_access_token

def test_websocket_ping_pong():
    token = create_access_token({"sub": "user_ws_test_123"})
    client = TestClient(app)
    
    with client.websocket_connect(f"/ws/v1/sessions/session-456?token={token}") as websocket:
        # 1. First message is connection_ack
        ack = websocket.receive_json()
        assert ack["type"] == "connection_ack"
        assert ack["session_id"] == "session-456"

        # 2. Send ping, receive pong
        websocket.send_json({"type": "ping"})
        reply = websocket.receive_json()
        assert reply["type"] == "pong"
        assert "timestamp" in reply

        # 3. Send test echo event
        websocket.send_json({"type": "test_echo", "data": {"message": "hello socket"}})
        echo_reply = websocket.receive_json()
        assert echo_reply["type"] == "test_echo_reply"
        assert echo_reply["data"]["message"] == "hello socket"

