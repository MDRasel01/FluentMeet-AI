"""
FluentMeet AI - Step 06 Test Suite: Security & Tenant Isolation
Specification: Step 06 - Section 20 & 21 (REQ-ING-018, REQ-ING-019)
"""

import pytest
from starlette.testclient import TestClient
from starlette.websockets import WebSocketDisconnect
from app.main import app
from app.core.security import create_access_token

class TestAudioSecurity:
    def test_reject_unauthorized_origin(self):
        client = TestClient(app)
        token = create_access_token({"sub": "user-origin-test"})
        # Connect with an untrusted origin
        headers = {"Origin": "http://malicious-attacker-domain.com"}
        with pytest.raises(Exception):
            with client.websocket_connect(f"/ws/v1/sessions/session-origin?token={token}", headers=headers) as ws:
                ws.receive_json()

    def test_allow_chrome_extension_origin(self):
        client = TestClient(app)
        token = create_access_token({"sub": "user-ext-test"})
        headers = {"Origin": "chrome-extension://abcdefghijklmnop"}
        with client.websocket_connect(f"/ws/v1/sessions/session-ext?token={token}", headers=headers) as ws:
            ack = ws.receive_json()
            assert ack["type"] == "connection_ack"

    def test_reject_invalid_token(self):
        client = TestClient(app)
        # Invalid signature or expired token
        with pytest.raises(Exception):
            with client.websocket_connect("/ws/v1/sessions/session-bad-token?token=invalid.jwt.token") as ws:
                ws.receive_json()

    def test_reject_unauthenticated_connection_in_production(self, monkeypatch):
        """Enforces DEF-001: Reject unauthenticated WebSocket connections when running in production."""
        from app.core.config import settings
        monkeypatch.setattr(settings, "APP_ENV", "production")
        client = TestClient(app)
        with pytest.raises(Exception):
            with client.websocket_connect("/ws/v1/sessions/session-no-token") as ws:
                ws.receive_json()
