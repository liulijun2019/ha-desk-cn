"""REST client for the desk HA backend (API Gateway + x-api-key)."""
from __future__ import annotations

import httpx


class DeskApiError(Exception):
    """Raised when the desk backend returns an error."""


class DeskApiClient:
    """Thin async client wrapping the three desk backend endpoints."""

    def __init__(self, base_url: str, api_key: str, account: str, password: str) -> None:
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._account = account
        self._password = password

    def _headers(self) -> dict[str, str]:
        return {"x-api-key": self._api_key, "Accept": "application/json"}

    async def list_devices(self) -> list[dict]:
        """GET /devices?account=...&password=... -> [{deviceId, thingName, account, status, deviceType}]."""
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(
                f"{self._base_url}/devices",
                params={"account": self._account, "password": self._password},
                headers=self._headers(),
            )
        resp.raise_for_status()
        return resp.json().get("devices", [])

    async def get_state(self, device_id: str) -> dict:
        """GET /devices/{deviceId}/state -> {deviceId, position, state, direction, ...}."""
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(
                f"{self._base_url}/devices/{device_id}/state",
                headers=self._headers(),
            )
        resp.raise_for_status()
        return resp.json()

    async def command(
        self,
        device_id: str,
        *,
        position: int | None = None,
        command: str | None = None,
        head_position: int | None = None,
        foot_position: int | None = None,
    ) -> None:
        """POST /devices/{deviceId}/command.

        desk/curtain: position 或 command=stop。
        bed: head_position / foot_position（可同时）。
        """
        payload: dict = {}
        if command == "stop":
            payload["command"] = "stop"
        elif head_position is not None or foot_position is not None:
            if head_position is not None:
                payload["headPosition"] = head_position
            if foot_position is not None:
                payload["footPosition"] = foot_position
        elif position is not None:
            payload["position"] = position
        else:
            raise ValueError("position / command / head_position / foot_position required")

        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(
                f"{self._base_url}/devices/{device_id}/command",
                json=payload,
                headers=self._headers(),
            )
        resp.raise_for_status()
