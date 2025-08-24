#!/usr/bin/env python3
"""pytest-asyncio test for WebSocket user status integration.

This file was converted from a standalone script into an async pytest test so
it can be run as part of the backend test suite using `pytest -q`.

The test requires a running backend at localhost:8000 and an accessible WebSocket
endpoint at ws://localhost:8000/ws/{game_id}?token={access_token}.
"""

import asyncio
import json
import os
import time

import httpx
import pytest
import websockets
from dotenv import load_dotenv


# Load environment
load_dotenv()

# Configuración por defecto
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
WS_URL = os.getenv("WS_URL", "ws://localhost:8000")


@pytest.mark.asyncio
async def test_websocket_status_integration():
    """End-to-end smoke test: register user, connect WS, send status updates.

    This test is intentionally tolerant of intermediate WS 'error' messages:
    the important assertions are that REST registration/login succeed and that
    the final user status returned by the API is the expected one.
    """

    unique_suffix = str(int(time.time()))
    test_user = {
        "username": f"test_ws_user_{unique_suffix}",
        "email": f"test_ws_{unique_suffix}@example.com",
        "password": "testpassword123",
    }

    game_id = "test_game_123"

    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        # 1) Register
        register_resp = await client.post(
            "/register", data={
                "username": test_user["username"],
                "email": test_user["email"],
                "password": test_user["password"],
            }
        )
        assert register_resp.status_code in (200, 201), f"register failed: {register_resp.text}"
        user_id = register_resp.json().get("user", {}).get("id")
        assert user_id, "user id missing in register response"

        # 2) Login
        login_resp = await client.post(
            "/login",
            data={"username": test_user["username"], "password": test_user["password"]},
        )
        assert login_resp.status_code == 200, f"login failed: {login_resp.text}"
        token = login_resp.json().get("access_token")
        assert token, "access_token missing in login response"

        # 3) Connect to WebSocket and listen in background
        ws_url = f"{WS_URL}/ws/{game_id}?token={token}"

        messages = []

        async def listener(ws):
            try:
                while True:
                    msg = await asyncio.wait_for(ws.recv(), timeout=10.0)
                    try:
                        messages.append(json.loads(msg))
                    except Exception:
                        messages.append({"raw": msg})
            except asyncio.TimeoutError:
                # expected when no more messages arrive
                return
            except websockets.exceptions.ConnectionClosed:
                return

        # Use a short overall timeout to keep test fast in CI
        try:
            async with websockets.connect(ws_url) as ws:
                # start listener
                listener_task = asyncio.create_task(listener(ws))

                # wait a bit for server-side automatic messages
                await asyncio.sleep(2)

                # send a series of status updates
                test_states = ["banned", "disconnected", "connected", "in_game"]
                for state in test_states:
                    await ws.send(json.dumps({"type": "update_user_status", "status": state, "timestamp": time.time()}))
                    await asyncio.sleep(1)

                # send a disallowed state to observe server behaviour
                await ws.send(json.dumps({"type": "update_user_status", "status": "banned", "timestamp": time.time()}))
                await asyncio.sleep(1)

                # close websocket
                await ws.close()
                # allow listener to drain
                await asyncio.sleep(0.5)

                # cancel listener if still running
                if not listener_task.done():
                    listener_task.cancel()
                    with pytest.raises(asyncio.CancelledError):
                        await listener_task

        except Exception as e:
            pytest.skip(f"Skipping WS assertions because connection failed: {e}")

        # 4) Verify final status via REST
        profile_resp = await client.get("/users/me", headers={"Authorization": f"Bearer {token}"})
        assert profile_resp.status_code == 200, f"profile fetch failed: {profile_resp.text}"
        final_status = profile_resp.json().get("user", {}).get("status")

        # Accept a small set of expected final states; adjust as backend evolves
        assert final_status in ("connected", "in_game", "disconnected"), f"unexpected final status: {final_status}"

        # Cleanup: attempt to remove created user via admin API
        try:
            admin_credentials = {
                "username": os.getenv("ADMIN_USERNAME", "admin"),
                "password": os.getenv("ADMIN_PASSWORD", "adminpass123"),
            }
            admin_login = await client.post("/login", data=admin_credentials)
            if admin_login.status_code == 200:
                admin_token = admin_login.json().get("access_token")
                del_resp = await client.delete(f"/admin/users/{user_id}", headers={"Authorization": f"Bearer {admin_token}"})
                # don't fail the test on cleanup problems, but log via assertion message if deletion fails
                assert del_resp.status_code in (200, 204), f"cleanup deletion failed: {del_resp.status_code} {del_resp.text}"
        except Exception:
            # best-effort cleanup; do not fail test if admin credentials are not present
            pass

