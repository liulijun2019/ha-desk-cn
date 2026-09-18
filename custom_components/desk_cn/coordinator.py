"""Coordinator that polls device list + per-device state."""
from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import DeskApiClient
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class DeskCoordinator(DataUpdateCoordinator[dict[str, dict]]):
    """Fetch every device under the account and its shadow state, keyed by deviceId."""

    def __init__(self, hass: HomeAssistant, api: DeskApiClient, poll_interval: int) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=poll_interval),
        )
        self.api = api

    async def _async_update_data(self) -> dict[str, dict]:
        try:
            devices = await self.api.list_devices()
        except Exception as exc:  # pylint: disable=broad-except
            raise UpdateFailed(f"list devices failed: {exc}") from exc

        states: dict[str, dict] = {}
        for dev in devices:
            device_id = dev["deviceId"]
            try:
                states[device_id] = await self.api.get_state(device_id)
            except Exception as exc:  # pylint: disable=broad-except
                _LOGGER.warning("failed to fetch state for %s: %s", device_id, exc)
                states[device_id] = {"deviceId": device_id, "online": False}
        return states
