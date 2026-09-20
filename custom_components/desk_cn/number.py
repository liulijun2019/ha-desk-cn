"""Number platform: bed head/foot (0-100) + desk height (72-120 cm)."""
from __future__ import annotations

from homeassistant.components.number import NumberEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DESK_HEIGHT_MAX, DESK_HEIGHT_MIN, DOMAIN
from .coordinator import DeskCoordinator

_PART_FIELD = {
    "head": "headPosition",
    "foot": "footPosition",
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up number entities (desk height + bed head/foot)."""
    coordinator: DeskCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities = []
    for device_id, state in coordinator.data.items():
        device_type = state.get("deviceType")
        if device_type == "bed":
            for part in ("head", "foot"):
                entities.append(DeskBedNumber(coordinator, device_id, part))
        elif device_type == "desk":
            entities.append(DeskHeightNumber(coordinator, device_id))
    async_add_entities(entities)


class DeskBedNumber(CoordinatorEntity, NumberEntity):
    """Represent a bed head/foot position as a number (0-100)."""

    _attr_native_min_value = 0
    _attr_native_max_value = 100
    _attr_native_step = 1.0

    def __init__(self, coordinator: DeskCoordinator, device_id: str, part: str) -> None:
        super().__init__(coordinator)
        self._device_id = device_id
        self._part = part
        self._field = _PART_FIELD[part]
        self._attr_name = f"{device_id} {part}"
        self._attr_unique_id = f"{DOMAIN}_{device_id}_{self._field}"

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
    def native_value(self) -> float | None:
        value = self._device_state.get(self._field)
        return float(value) if value is not None else None

    async def async_set_native_value(self, value: float) -> None:
        """Send the new head/foot position to the device."""
        if self._field == "headPosition":
            await self.coordinator.api.command(self._device_id, head_position=int(value))
        else:
            await self.coordinator.api.command(self._device_id, foot_position=int(value))
        await self.coordinator.async_request_refresh()


class DeskHeightNumber(CoordinatorEntity, NumberEntity):
    """Represent a desk height (72-120 cm) as a number."""

    _attr_native_min_value = DESK_HEIGHT_MIN
    _attr_native_max_value = DESK_HEIGHT_MAX
    _attr_native_step = 1.0
    _attr_native_unit_of_measurement = "cm"

    def __init__(self, coordinator: DeskCoordinator, device_id: str) -> None:
        super().__init__(coordinator)
        self._device_id = device_id
        self._attr_name = f"{device_id} height"
        self._attr_unique_id = f"{DOMAIN}_{device_id}_height"

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
    def native_value(self) -> float | None:
        value = self._device_state.get("position")
        return float(value) if value is not None else None

    async def async_set_native_value(self, value: float) -> None:
        """Send the new desk height to the device."""
        await self.coordinator.api.command(self._device_id, position=int(value))
        await self.coordinator.async_request_refresh()
