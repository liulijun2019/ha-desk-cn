"""Cover platform: each curtain becomes a cover entity."""
from __future__ import annotations

from homeassistant.components.cover import (
    ATTR_POSITION,
    CoverEntity,
    CoverEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import DeskCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up cover entities (curtain only)."""
    coordinator: DeskCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities = [
        DeskCover(coordinator, device_id)
        for device_id, state in coordinator.data.items()
        if state.get("deviceType") == "curtain"
    ]
    async_add_entities(entities)


class DeskCover(CoordinatorEntity, CoverEntity):
    """Represent a curtain as a HA cover."""

    def __init__(self, coordinator: DeskCoordinator, device_id: str) -> None:
        super().__init__(coordinator)
        self._device_id = device_id
        self._attr_name = device_id
        self._attr_unique_id = f"{DOMAIN}_{device_id}"

    @property
    def _device_state(self) -> dict:
        return self.coordinator.data.get(self._device_id, {})

    @property
    def device_info(self) -> DeviceInfo:
        """Return device registry info."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._device_id)},
            name=self._device_id,
            manufacturer="Desk",
            model=self._device_state.get("model"),
            sw_version=self._device_state.get("firmware"),
        )

    @property
    def supported_features(self) -> CoverEntityFeature:
        return (
            CoverEntityFeature.OPEN
            | CoverEntityFeature.CLOSE
            | CoverEntityFeature.SET_POSITION
            | CoverEntityFeature.STOP
        )

    @property
    def current_cover_position(self) -> int | None:
        pos = self._device_state.get("position")
        return int(pos) if pos is not None else None

    @property
    def is_closed(self) -> bool:
        pos = self._device_state.get("position")
        return pos is not None and int(pos) <= 0

    @property
    def is_opening(self) -> bool:
        return self._device_state.get("state") == "moving" and self._device_state.get("direction") == "up"

    @property
    def is_closing(self) -> bool:
        return self._device_state.get("state") == "moving" and self._device_state.get("direction") == "down"

    async def async_open_cover(self, **kwargs) -> None:
        await self._command(position=100)

    async def async_close_cover(self, **kwargs) -> None:
        await self._command(position=0)

    async def async_set_cover_position(self, **kwargs) -> None:
        position = kwargs.get(ATTR_POSITION)
        if position is not None:
            await self._command(position=int(position))

    async def async_stop_cover(self, **kwargs) -> None:
        await self._command(command="stop")

    async def _command(self, *, position: int | None = None, command: str | None = None) -> None:
        await self.coordinator.api.command(self._device_id, position=position, command=command)
        await self.coordinator.async_request_refresh()
